class UKVisaExpertSystem:
    def __init__(self):
        self.facts = {}
        self.diagnosis = None
        self.triggered_rules = []

    def gather_facts(self):
        print("\n--- UK Visa Eligibility Assessment ---")
        print("Please answer the following questions to determine your visa pathway.\n")

        self.facts['purpose'] = input("1. What is the main purpose of your visit? (tourism/study/work/transit/join family): ").strip().lower()
        
        if self.facts['purpose'] in ['tourism', 'study', 'work']:
            self.facts['duration'] = input("2. Will your stay be over 6 months? (yes/no): ").strip().lower()
            
            if self.facts['purpose'] == 'tourism' and self.facts['duration'] == 'no':
                treatment = input("   Are you visiting for medical treatment? (yes/no): ").strip().lower()
                if treatment == 'yes':
                    self.facts['purpose'] = 'medical treatment'
                    self.facts['duration_months'] = int(input("   How many months do you need for treatment?: "))
        
        if self.facts['purpose'] == 'study':
            self.facts['age'] = int(input("3. What is your age?: "))
            if self.facts['duration'] == 'yes':
                self.facts['course_type'] = input("4. Is the course higher education or independent school? (higher education/independent school): ").strip().lower()
                self.facts['english_proof'] = input("5. Do you have proof of English language proficiency? (yes/no): ").strip().lower()
                self.facts['financial_proof'] = input("6. Do you have proof of financial support? (yes/no): ").strip().lower()

        if self.facts['purpose'] == 'work':
            self.facts['job_offer'] = input("3. Do you have a confirmed job offer? (yes/no): ").strip().lower()
            self.facts['employer_sponsorship'] = input("4. Do you have a licensed employer sponsor? (yes/no): ").strip().lower()
            if self.facts['duration'] == 'no':
                self.facts['work_type'] = input("5. What type of work? (charity/creative/other): ").strip().lower()

        if self.facts['purpose'] == 'transit':
            self.facts['border_control'] = input("2. Will you pass through UK border control? (yes/no): ").strip().lower()

        if self.facts['purpose'] == 'join family':
            self.facts['family_status'] = input("2. What is the status of your family member? (uk citizen/temporary resident): ").strip().lower()
            self.facts['relationship'] = input("3. What is your relationship to them? (spouse/child/other): ").strip().lower()

        print("\n--- Background Checks ---")
        self.facts['criminal_record'] = input("Do you have a severe criminal record? (yes/no): ").strip().lower()
        self.facts['previous_refusal'] = input("Have you had a previous visa refusal that you hid on this application? (yes/no): ").strip().lower()

    def inference_engine(self):
        if self.facts.get('criminal_record') == 'yes':
            self.diagnosis = "Application Rejected - General Grounds for Refusal (High Severity Offense)"
            self.triggered_rules.append("R19")
            return
        if self.facts.get('previous_refusal') == 'yes':
            self.diagnosis = "Application Rejected - Deception"
            self.triggered_rules.append("R20")
            return

        # Tourism & Visiting Rules
        if self.facts.get('purpose') == 'tourism' and self.facts.get('duration') == 'no':
            self.diagnosis = "Standard Visitor Visa"
            self.triggered_rules.append("R01")
        elif self.facts.get('purpose') == 'medical treatment' and self.facts.get('duration_months', 0) <= 11:
            self.diagnosis = "Standard Visitor Visa for Medical Treatment"
            self.triggered_rules.append("R03")
        elif self.facts.get('purpose') == 'tourism' and self.facts.get('duration') == 'yes':
            self.diagnosis = "Application Rejected - Duration Exceeds Tourist Limit"
            self.triggered_rules.append("R04")

        # Study Rules
        elif self.facts.get('purpose') == 'study':
            if self.facts.get('duration') == 'no':
                self.diagnosis = "Standard Visitor Visa"
                self.triggered_rules.append("R05")
            elif self.facts.get('english_proof') == 'no':
                self.diagnosis = "Application Rejected - Language Requirement Failed"
                self.triggered_rules.append("R08")
            elif self.facts.get('financial_proof') == 'no':
                self.diagnosis = "Application Rejected - Financial Requirement Failed"
                self.triggered_rules.append("R09")
            elif self.facts.get('duration') == 'yes' and self.facts.get('age', 0) >= 16 and self.facts.get('course_type') == 'higher education':
                self.diagnosis = "Student Visa"
                self.triggered_rules.append("R06")
            elif self.facts.get('duration') == 'yes' and self.facts.get('age', 0) < 16 and self.facts.get('course_type') == 'independent school':
                self.diagnosis = "Child Student Visa"
                self.triggered_rules.append("R07")

        # Work Rules
        elif self.facts.get('purpose') == 'work':
            if self.facts.get('job_offer') == 'no':
                self.diagnosis = "Application Rejected - Job Offer Required"
                self.triggered_rules.append("R11")
            elif self.facts.get('employer_sponsorship') == 'no':
                self.diagnosis = "Application Rejected - Licensed Sponsor Required"
                self.triggered_rules.append("R14")
            elif self.facts.get('duration') == 'yes' and self.facts.get('job_offer') == 'yes' and self.facts.get('employer_sponsorship') == 'yes':
                self.diagnosis = "Skilled Worker Visa"
                self.triggered_rules.append("R10")
            elif self.facts.get('duration') == 'no' and self.facts.get('work_type') == 'charity':
                self.diagnosis = "Temporary Worker - Charity Worker Visa"
                self.triggered_rules.append("R12")
            elif self.facts.get('duration') == 'no' and self.facts.get('work_type') == 'creative':
                self.diagnosis = "Temporary Worker - Creative and Sporting Visa"
                self.triggered_rules.append("R13")

        # Transit & Family Rules
        elif self.facts.get('purpose') == 'transit':
            if self.facts.get('border_control') == 'yes':
                self.diagnosis = "Visitor in Transit Visa"
                self.triggered_rules.append("R15")
            elif self.facts.get('border_control') == 'no':
                self.diagnosis = "Direct Airside Transit Visa"
                self.triggered_rules.append("R16")

        elif self.facts.get('purpose') == 'join family':
            if self.facts.get('family_status') == 'uk citizen' and self.facts.get('relationship') == 'spouse':
                self.diagnosis = "Family Visa (Spouse)"
                self.triggered_rules.append("R17")
            elif self.facts.get('family_status') == 'temporary resident':
                self.diagnosis = "Dependent Visa"
                self.triggered_rules.append("R18")

        # Fallback
        if not self.diagnosis:
            self.diagnosis = "Unable to determine visa pathway. Please consult UKVI directly."

    def display_results(self):
        print("\n=========================================")
        print("           ASSESSMENT RESULT             ")
        print("=========================================")
        print(f"Recommended Pathway : {self.diagnosis}")
        if self.triggered_rules:
            print(f"Rule(s) Triggered   : {', '.join(self.triggered_rules)}")
        print("=========================================")
        print("Disclaimer: This is an educational expert system, not legal advice.")


if __name__ == "__main__":
    system = UKVisaExpertSystem()
    system.gather_facts()
    system.inference_engine()
    system.display_results()
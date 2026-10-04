:- use_module(library(http/thread_httpd)).
:- use_module(library(http/http_dispatch)).
:- use_module(library(http/http_json)).
:- use_module(library(http/http_files)).

% Start the server on port 8080 (Run this by typing: server(8080).)
server(Port) :-
    http_server(http_dispatch, [port(Port)]).

% Route: Serve the HTML GUI
:- http_handler(root(.), serve_index, []).
serve_index(Request) :-
    http_reply_file('index.html', [], Request).

% Route: Handle the assessment API request from the web GUI
:- http_handler('/api/assess', handle_assess, []).

:- dynamic known/2.

handle_assess(Request) :-
    http_read_json_dict(Request, Dict),
    % Clear working memory for the new request
    retractall(known(_, _)),
    
    % Convert JSON dictionary to Prolog facts and assert them
    dict_pairs(Dict, _, Pairs),
    maplist(assert_fact, Pairs),
    
    % Run the inference engine
    (   visa(Outcome, RuleID)
    ->  Reply = _{outcome: Outcome, rule: RuleID}
    ;   Reply = _{outcome: 'Unable to determine visa pathway based on inputs.', rule: 'N/A'}
    ),
    reply_json(Reply).

% Helper to assert facts dynamically from JSON
assert_fact(Key-Value) :-
    % Convert strings from JSON to atoms so they match the rules
    atom_string(AtomValue, Value),
    assertz(known(Key, AtomValue)).

% The modified value/2 predicate for the web (checks memory, doesn't prompt console)
value(Attribute, Value) :-
    known(Attribute, Value).

% =========================================================
% KNOWLEDGE BASE: 20 RULES
% =========================================================

% General Refusals (Highest Priority)
visa('Application Rejected - General Grounds for Refusal', 'R19') :- value(criminal_record, yes).
visa('Application Rejected - Deception', 'R20') :- value(previous_refusal_hidden, yes).

% Tourism & Visiting Rules
visa('Standard Visitor Visa', 'R01') :- value(purpose, tourism), value(duration_over_6_months, no).
visa('Standard Visitor Visa', 'R02') :- value(purpose, visit_family), value(duration_over_6_months, no).
visa('Standard Visitor Visa for Medical Treatment', 'R03') :- value(purpose, medical), value(duration_over_6_months, no).
visa('Application Rejected - Duration Exceeds Tourist Limit', 'R04') :- value(purpose, tourism), value(duration_over_6_months, yes).

% Study Rules
visa('Standard Visitor Visa', 'R05') :- value(purpose, study), value(duration_over_6_months, no).
visa('Student Visa', 'R06') :- value(purpose, study), value(duration_over_6_months, yes), value(age_over_16, yes), value(course_type, higher_education), value(english_proof, yes), value(financial_proof, yes).
visa('Child Student Visa', 'R07') :- value(purpose, study), value(duration_over_6_months, yes), value(age_over_16, no), value(course_type, independent_school).
visa('Application Rejected - Language Requirement Failed', 'R08') :- value(purpose, study), value(duration_over_6_months, yes), value(english_proof, no).
visa('Application Rejected - Financial Requirement Failed', 'R09') :- value(purpose, study), value(duration_over_6_months, yes), value(financial_proof, no).

% Work Rules
visa('Skilled Worker Visa', 'R10') :- value(purpose, work), value(duration_over_6_months, yes), value(job_offer, yes), value(employer_sponsorship, yes).
visa('Application Rejected - Job Offer Required', 'R11') :- value(purpose, work), value(job_offer, no).
visa('Temporary Worker - Charity Worker Visa', 'R12') :- value(purpose, work), value(duration_over_6_months, no), value(work_type, charity).
visa('Temporary Worker - Creative and Sporting Visa', 'R13') :- value(purpose, work), value(duration_over_6_months, no), value(work_type, creative).
visa('Application Rejected - Licensed Sponsor Required', 'R14') :- value(purpose, work), value(employer_sponsorship, no).

% Transit & Family Rules
visa('Visitor in Transit Visa', 'R15') :- value(purpose, transit), value(border_control, yes).
visa('Direct Airside Transit Visa', 'R16') :- value(purpose, transit), value(border_control, no).
visa('Family Visa (Spouse)', 'R17') :- value(purpose, join_family), value(family_status, uk_citizen), value(relationship, spouse).
visa('Dependent Visa', 'R18') :- value(purpose, join_family), value(family_status, temporary_resident).
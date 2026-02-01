"""
Comprehensive Mock Client Data
Based on realistic UK Financial Advisor sample documents
"""

from datetime import date, datetime, timedelta
from typing import List
import json

from schema import (
    Client, ClientDatabase, ContactInfo, Address, FamilyMember,
    LifeEvent, Concern, Policy, RiskProfile, MeetingNote, 
    FollowUp, Interaction, ComplianceRecord,
    ContactMethod, RiskAttitude, PolicyType, ConcernSeverity,
    ConcernStatus, FollowUpStatus, LifeEventType
)


def create_sarah_michael_thompson() -> Client:
    """
    Sarah & Michael Thompson - High-earning couple, private school fees,
    retirement planning focus, DB pension, multiple concerns
    """
    return Client(
        id="CLT-2024001",
        title="Mrs",
        first_name="Sarah",
        last_name="Thompson",
        date_of_birth=date(1978, 3, 12),
        national_insurance="AB123456C",
        occupation="Senior Marketing Manager",
        employer="Unilever UK Ltd",
        annual_income=103000,
        contact_info=ContactInfo(
            email="sarah.thompson@gmail.com",
            phone="01234 567890",
            mobile="07712 345678",
            address=Address(
                line1="47 Meadowbrook Lane",
                city="Weybridge",
                county="Surrey",
                postcode="KT13 9PL"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Morning"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Michael",
                relationship="spouse",
                date_of_birth=date(1976, 7, 24),
                notes="Associate Architect at Sterling Architects Ltd, £72k salary, mild hypertension controlled with medication"
            ),
            FamilyMember(
                name="Emily",
                relationship="child",
                date_of_birth=date(2010, 6, 18),
                notes="Age 14, St Catherine's School Weybridge, academically gifted, predicted A*/A grades, wants to study medicine or veterinary science"
            ),
            FamilyMember(
                name="Oliver",
                relationship="child",
                date_of_birth=date(2013, 9, 3),
                notes="Age 11, St Catherine's School, more creative like Michael, interested in art and design"
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 9, 1),
                description="Emily starting GCSEs - potential tutoring costs",
                related_person="Emily",
                source="fact_find"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2028, 9, 1),
                description="Emily starting university - estimated £40k funding needed",
                related_person="Emily",
                source="fact_find"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 3, 1),
                description="Mortgage fixed rate expires - needs review before March 2026",
                source="fact_find"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2027, 6, 1),
                description="Family holiday to Australia planned - budget £15,000, visiting Sarah's emigrated best friend",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="retirement savings adequacy",
                details="Sarah feels 'behind' on pension savings compared to colleagues. Concerned whether they're saving enough for retirement. Target retirement: Sarah 60, Michael 62 with £50-60k combined income.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 11, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 11, 15)
            ),
            Concern(
                topic="inheritance tax liability",
                details="Surprised by estimated £160k IHT liability. Both from middle-class backgrounds, not used to estate planning. Don't want to burden children with IHT bill.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 11, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 11, 15)
            ),
            Concern(
                topic="children's education funding",
                details="Very focused on Emily and Oliver's education. Private school fees £2,600/month. University costs estimated £40k per child. Emily academically gifted, may study medicine (5-6 years).",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 11, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 11, 15)
            ),
            Concern(
                topic="protection gap - Michael",
                details="Michael has no critical illness cover and no income protection beyond statutory sick pay. Father died at 68 of heart attack. Michael has hypertension. May face underwriting issues.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 11, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 11, 15)
            ),
            Concern(
                topic="mortgage strategy",
                details="Current fixed rate expires March 2026. Outstanding £287k @ 3.89%. Need to review options before expiry.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 11, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 11, 15)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Unilever UK Pension Fund",
                policy_number="UNI-DB-2016-ST",
                current_value=412000,  # Transfer value
                monthly_contribution=0,  # DB scheme
                start_date=date(2016, 3, 1),
                notes="Defined Benefit - Final Salary. Accrual 1/60th. 8 years service. Projected £28k/year at 65. 50% spouse pension. DO NOT TRANSFER - extremely valuable."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Aviva",
                policy_number="SIPP-AV-2008-ST",
                current_value=87400,
                monthly_contribution=0,
                start_date=date(2008, 1, 1),
                notes="Previous employer WPP Group 2008-2016. Vanguard LifeStrategy 60%. Charges 0.41%."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="ISA-VG-ST",
                current_value=47320,
                monthly_contribution=400,
                notes="LifeStrategy 80% Equity. Sarah manages own investments, reads FT and Monevator."
            ),
            Policy(
                policy_type=PolicyType.LIFE_INSURANCE,
                provider="Aviva",
                policy_number="LIFE-AV-ST-500",
                current_value=500000,
                monthly_contribution=45,
                renewal_date=date(2038, 1, 1),
                notes="Level Term Assurance. 20 year term expires 2038. Includes £150k Critical Illness. In trust for Michael and children."
            )
        ],
        total_portfolio_value=1099770,  # Net worth from fact-find
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.HIGH,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="extensive",
            time_horizon_years=15,
            last_assessed=date(2024, 11, 15),
            notes="Sarah: 7/10 Adventurous/Growth. Managed own ISAs 10+ years. Read Tim Hale's Smarter Investing. Comfortable with volatility. Michael: 6/10 Balanced/Growth, slightly more cautious."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2024, 11, 15),
                meeting_type=ContactMethod.IN_PERSON,
                duration_minutes=135,
                summary="Initial comprehensive fact-find meeting at client's home. Both well-prepared with documentation. Sarah took lead but Michael fully engaged. Triggered to act after friends recommended firm. Recent 40th+ birthdays focused minds on retirement.",
                transcript="""Key discussion points:

RETIREMENT: Sarah ideally retire 58-60, feeling 'burned out' at times from intense Unilever pace. Michael more flexible, enjoys work but wants reduced hours from 60. Want to travel (Australia, NZ, Japan), spend time with future grandchildren. Concerned £50k/year may not be enough - will model £60k scenarios.

PROPERTY: Love Weybridge home, no plans to move unless downsizing in retirement. House valued £875k (paid £495k in 2012). Mentioned possible retirement to Winchester (near Sarah's sister Emma) or Devon/Cornwall.

PROTECTION: Both understand importance given mortgage and children. Sarah has excellent employer benefits. Critical gap: Michael has NO critical illness cover and NO income protection. Michael's father died age 68 (heart attack). Michael has hypertension - seemed uncomfortable discussing, Sarah had to encourage sharing. URGENT recommendation for CI cover but expect underwriting issues.

WILLS/LPA: Current wills from 2019, need update. No LPAs in place - significant gap.

INVESTMENTS: Sarah knowledgeable, follows Monevator, read Tim Hale. Comfortable with passive approach. 80/20 equity/bond split appropriate. Michael less engaged but trusts Sarah. His workplace pension in default fund never reviewed - opportunity. Both interested in ESG but not strict ethical.

CHILDREN: Emily (14) very academic, predicted straight As, wants medicine/vet. Oliver (11) more creative like Michael. School fees £2,600/month committed until sixth form. JISAs: Emily £18.4k, Oliver £14.2k.""",
                key_points=[
                    "Sarah feeling burned out at Unilever, wants to retire by 60",
                    "Michael's father died age 68 of heart attack - family history concern",
                    "Michael has NO critical illness cover or income protection - URGENT",
                    "Wills from 2019 need update, NO LPAs in place",
                    "Emily predicted A*/A grades, wants to study medicine",
                    "Mortgage fixed rate expires March 2026 - needs review"
                ],
                action_items=[
                    "Prepare comprehensive suitability report",
                    "Pension consolidation review for Michael",
                    "Get CI quotes for Michael (expect underwriting loadings)",
                    "Review mortgage strategy before March 2026",
                    "Recommend wills update and LPAs",
                    "University funding projection"
                ],
                concerns_raised=["retirement savings adequacy", "inheritance tax liability", "protection gap - Michael"],
                life_events_mentioned=["Emily starting GCSEs", "Australia trip planned", "Mortgage expires March 2026"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Prepare comprehensive suitability report covering retirement, pension consolidation, protection, university funding, tax and estate planning",
                deadline=date(2024, 12, 6),
                status=FollowUpStatus.PENDING,
                created_date=date(2024, 11, 15)
            ),
            FollowUp(
                commitment="Get critical illness quotes for Michael with full medical underwriting",
                deadline=date(2024, 11, 30),
                status=FollowUpStatus.PENDING,
                created_date=date(2024, 11, 15)
            ),
            FollowUp(
                commitment="Schedule follow-up meeting to present recommendations",
                deadline=date(2024, 12, 6),
                status=FollowUpStatus.PENDING,
                created_date=date(2024, 11, 15),
                notes="Meeting scheduled for 6th December 2024"
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2024, 11, 15, 10, 0),
                method=ContactMethod.IN_PERSON,
                direction="outbound",
                summary="Initial fact-find meeting at client's home, Weybridge. 2h15m comprehensive review.",
                duration_minutes=135,
                next_action="Prepare suitability report for 6th December meeting"
            ),
            Interaction(
                interaction_date=datetime(2024, 11, 10, 14, 30),
                method=ContactMethod.PHONE,
                direction="inbound",
                summary="Sarah called to confirm meeting and ask what documents to prepare",
                duration_minutes=10,
                next_action="Meeting confirmed for 15th November"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=None,
            next_review_due=date(2025, 11, 15),
            review_status="pending",
            suitability_confirmed=False,
            value_delivered=[],
            notes="New client as of November 2024. First annual review due November 2025."
        ),
        client_since=date(2024, 11, 10),
        assigned_advisor="Jonathan Hayes",
        tags=["high-value", "protection-focus", "retirement-planning", "db-pension"],
        notes="Excellent client engagement. Sarah financially literate, Michael fully engaged. Strong financial position but gaps to address. Retirement goals achievable with right planning. Good long-term planning client."
    )


def create_david_sarah_chen() -> Client:
    """
    David & Sarah Chen - Very high earners, investment banker, complex tax planning,
    French property aspirations, VCT investments, share options
    """
    return Client(
        id="CLT-2024003",
        title="Mr",
        first_name="David",
        last_name="Chen",
        date_of_birth=date(1975, 6, 12),
        national_insurance="CD345678D",
        occupation="Investment Banking Director",
        employer="Goldman Sachs",
        annual_income=245000,  # Salary + bonus
        contact_info=ContactInfo(
            email="david.chen@globalbank.com",
            phone="020 7123 4567",
            mobile="07789 234567",
            address=Address(
                line1="28 Riverside Court",
                city="Richmond",
                county="Greater London",
                postcode="TW9 1PQ"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Evening"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Sarah",
                relationship="spouse",
                date_of_birth=date(1977, 11, 8),
                notes="Arts Council Senior Manager, 4 days/week, £72k salary. Considering 3 days/week from 2026 (-£18k income). Had hypertension, now controlled at 125/78."
            ),
            FamilyMember(
                name="Oliver",
                relationship="child",
                date_of_birth=date(2008, 3, 14),
                notes="Age 16, Westminster School, applying to Oxbridge/Durham/Bristol for Economics. University September 2025."
            ),
            FamilyMember(
                name="Sophie",
                relationship="child",
                date_of_birth=date(2011, 9, 22),
                notes="Age 13, Westminster School. University 2029."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2025, 3, 15),
                description="David bonus £60k expected - recommend £20k VCT + £20k ISA + £20k pension carry-forward = £18k tax saved",
                source="meeting_notes"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2025, 3, 1),
                description="French property viewing trip to Luberon, Provence. £400k budget.",
                source="recommendation"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2025, 9, 1),
                description="Oliver starting university - if Oxbridge, costs £45k (vs £40k planned). JISA £28.4k with £12k/year supplement.",
                related_person="Oliver",
                source="meeting_notes"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 5, 1),
                description="Remortgage decision required - current fix expires May 2026. £285k @ 2.89%. If French property: increase to £585k.",
                source="fact_find"
            )
        ],
        concerns=[
            Concern(
                topic="work stress and career change",
                details="David working 70+ hours/week. Considering exit to consulting (£120k vs £245k current). Physical and mental fatigue at age 49.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 15)
            ),
            Concern(
                topic="tax efficiency - lost personal allowance",
                details="David: £220k adjusted income, lost all PA, paying 45% over £125k. Major inefficiency. VCT investment recommended for 30% relief.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 10, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2026, 1, 15),
                notes="Increased pension to 15% (saves £12,450 tax). VCT £30k/year pending."
            ),
            Concern(
                topic="market risk approaching retirement",
                details="£1M+ in equities, approaching retirement (9 years). Currently 75/25 allocation. Should de-risk to 60/40 at age 55.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2026, 1, 15)
            ),
            Concern(
                topic="French property - cross-border complexity",
                details="Planning £400k property in Provence. Currency risk (£/€), rental voids if not used, maintenance £10k/year. Residency implications if permanent move.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 1, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 15)
            ),
            Concern(
                topic="Sarah protection gap",
                details="Sarah CI cover £150k recommendation postponed - had hypertension (now controlled BP 125/78). Re-quote January 2025.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 12),
                notes="BP now controlled. Re-quoting in progress."
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Goldman Sachs SIPP",
                policy_number="GS-SIPP-DC",
                current_value=825000,  # Goldman £680k + consolidated Barclays £145k
                monthly_contribution=2312,  # 15% of £185k
                start_date=date(2012, 1, 1),
                notes="Increased contribution 8%→15% (Oct 2025). Saves £12,450 tax. Consolidated Barclays pension (£145k) Dec 2024, saves £1,200/year fees."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="LGPS",
                policy_number="LGPS-SC-DB",
                current_value=0,  # DB so no transfer value listed
                monthly_contribution=0,
                notes="Sarah's Defined Benefit - accrued £22k/year. Considering 3 days/week from 2026 would reduce accrual."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Fidelity",
                policy_number="SIPP-FID-SC",
                current_value=34000,
                monthly_contribution=200,
                notes="Sarah's SIPP from previous role."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="AJ Bell",
                policy_number="ISA-AJB-DC",
                current_value=185400,
                monthly_contribution=1666
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Hargreaves Lansdown",
                policy_number="ISA-HL-SC",
                current_value=142800,
                monthly_contribution=1000
            ),
            Policy(
                policy_type=PolicyType.LIFE_INSURANCE,
                provider="Aviva",
                policy_number="LIFE-AV-DC",
                current_value=750000,
                monthly_contribution=85,
                renewal_date=date(2035, 1, 1),
                notes="Includes £200k Critical Illness. In trust. Expires 2035."
            )
        ],
        total_portfolio_value=2850000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.HIGH,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="extensive",
            time_horizon_years=9,
            last_assessed=date(2025, 10, 1),
            notes="David very analytical (banking background), likes detailed projections. Currently 75/25 equity/bond. Should de-risk to 60/40 at 55. Both wine enthusiasts."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2026, 1, 15),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=60,
                summary="October 2025 review follow-up. David bonus £85k (above average). Sarah promoted to £72k. Oliver applying universities. Reviewed remortgage options and French property strategy.",
                key_points=[
                    "David bonus £85k - allocated £40k to mortgage, £45k to ISAs",
                    "Sarah promoted £65k → £72k",
                    "Oliver applying Oxbridge, Durham, Bristol for Economics",
                    "Sarah considering 3 days/week from 2026 (-£18k income)",
                    "French property viewing trip March 2025",
                    "Remortgage comparison sent - 5yr 4.1% or 10yr 4.4%"
                ],
                action_items=[
                    "Re-quote Sarah CI (BP now controlled)",
                    "David research VCT options (Feb 2025)",
                    "Remortgage decision (Feb 2025)",
                    "French viewing trip (March 2025)"
                ],
                concerns_raised=["work stress and career change", "French property - cross-border complexity"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Re-quote Sarah CI cover £150k - BP now controlled at 125/78",
                deadline=date(2026, 1, 31),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 12),
                notes="In progress - awaiting underwriter response"
            ),
            FollowUp(
                commitment="David VCT research and options presentation",
                deadline=date(2026, 2, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 15)
            ),
            FollowUp(
                commitment="Remortgage options presentation and decision",
                deadline=date(2026, 2, 28),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 15),
                notes="Current fix expires May 2026. Options: 5yr (4.1%) or 10yr (4.4%). If French property, increase to £585k."
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2026, 1, 21, 9, 0),
                method=ContactMethod.EMAIL,
                direction="inbound",
                summary="David email - bonus £60k confirmed for March",
                duration_minutes=0,
                next_action="Prepare bonus allocation recommendation"
            ),
            Interaction(
                interaction_date=datetime(2026, 1, 15, 14, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Review meeting - bonus allocation, French property, remortgage options",
                duration_minutes=60,
                next_action="Send remortgage comparison spreadsheet"
            ),
            Interaction(
                interaction_date=datetime(2026, 1, 12, 11, 30),
                method=ContactMethod.PHONE,
                direction="inbound",
                summary="Sarah call - CI re-quote discussion. BP now controlled.",
                duration_minutes=15,
                next_action="Re-quote CI with updated medical"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 10, 1),
            next_review_due=date(2026, 2, 18),
            review_status="due_soon",
            suitability_confirmed=True,
            suitability_date=date(2025, 10, 1),
            value_delivered=[
                "Pension contribution optimization 8%→15% - saves £12,450 tax annually",
                "Consolidated Barclays pension - saves £1,200/year fees",
                "Wills updated November 2024 - mirror wills, children at 25",
                "LPAs created and registered December 2024"
            ]
        ),
        client_since=date(2022, 3, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["high-value", "complex-tax", "vct-candidate", "cross-border"],
        notes="David very analytical (banking background), likes detailed projections. Sarah more lifestyle/family focused. Both wine enthusiasts. Chinese heritage - annual HK trips to see David's parents. Children academically gifted."
    )


def create_basil_sybil_fawlty() -> Client:
    """
    Basil & Sybil Fawlty - Semi-retired hotel owners, business exit planning,
    CGT considerations, Spain relocation aspirations
    """
    return Client(
        id="CLT-2024015",
        title="Mr",
        first_name="Basil",
        last_name="Fawlty",
        date_of_birth=date(1958, 5, 19),
        occupation="Hotel Owner/Operator (semi-retired)",
        employer="Fawlty Towers Hotel",
        annual_income=42500,  # Half of £85k business profit
        contact_info=ContactInfo(
            email="basil@fawltytowers.co.uk",
            phone="01803 123456",
            mobile="07789 234567",
            address=Address(
                line1="Fawlty Towers Hotel",
                line2="Torquay Seafront",
                city="Torquay",
                county="Devon",
                postcode="TQ1 2BE"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Morning"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Sybil",
                relationship="spouse",
                date_of_birth=date(1960, 8, 7),
                notes="Age 65, co-owner Fawlty Towers. Pragmatic, fatigued, focused on quality of life. Increasingly keen to exit hotel regardless of price."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.RETIREMENT,
                event_date=date(2027, 6, 1),
                description="Target hotel exit during 2026-27 window. Sale preferred but lease option available.",
                source="planning_discussion"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 4, 5),
                description="CGT Business Asset Disposal Relief deadline - strong incentive to complete sale before any legislative changes. Estimated gain £925k, BADR at 10% = £92,500 tax.",
                source="tax_planning"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 3, 1),
                description="Continued Spain winter rentals - purchase target £120k if hotel sold. Residency/healthcare implications need addressing.",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="hotel sale delay",
                details="Hotel remains unsold after 2024-25 listing at £1.45M. Market feedback: £1.2-1.3M realistic. Basil resistant to price reduction despite market evidence. Illiquidity and over-pricing delaying exit.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 21),
                notes="Basil ego-attached to hotel as life's work. Sybil pragmatic, fatigued."
            ),
            Concern(
                topic="potential loss of BADR",
                details="Business Asset Disposal Relief at 10% could save £92,500 on £925k estimated gain. If sale delayed and legislation changes, tax liability materially increases. URGENT - key lever to unlock Basil's decision.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 1, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 21)
            ),
            Concern(
                topic="physical and mental fatigue",
                details="Both aged 67/65, running 12-room hotel is physically demanding. Winter closures (Dec-Feb) reinforce desire to retire. Health impacts of prolonged stress.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 1, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 21)
            ),
            Concern(
                topic="estate planning gaps",
                details="Current wills from 1995 - 30 years out of date. No LPAs in place. Cross-border estate considerations if Spain residency pursued.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2026, 1, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2026, 1, 21)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Standard Life",
                policy_number="SIPP-SL-BF",
                current_value=285000,
                monthly_contribution=0,
                notes="Basil's SIPP. No current contributions."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Aviva",
                policy_number="PP-AV-SF",
                current_value=165000,
                monthly_contribution=0,
                notes="Sybil's personal pension."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="ISA-VG-JOINT",
                current_value=145000,
                monthly_contribution=0,
                notes="Joint ISAs. Not currently contributing due to business cashflow needs."
            )
        ],
        total_portfolio_value=2100000,  # Including hotel value
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.MEDIUM,
            investment_experience="moderate",
            time_horizon_years=5,
            last_assessed=date(2026, 1, 1),
            notes="Post-retirement, income drawdown flexibility needed. Target £65k/year retirement income."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2026, 1, 21),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=45,
                summary="January 2026 review. Hotel still unsold. Market consensus £1.2-1.3M. Basil still believes £1.45M achievable despite evidence. Sybil increasingly frustrated. Discussed lease option as interim bridge.",
                key_points=[
                    "Hotel unsold - market feedback £1.2-1.3M realistic",
                    "Basil resistant to price reduction",
                    "Sybil renewed frustration over delayed sale",
                    "Lease option: 10-year ~£48k/year indexed",
                    "Spanish winter rental repeated positively",
                    "BADR eligibility critical - 10% vs higher rate"
                ],
                action_items=[
                    "Confirm BADR eligibility and legislative status",
                    "Revisit sale price with updated market evidence",
                    "Progress wills and LPAs urgently",
                    "Spain residency and tax planning clarification"
                ],
                concerns_raised=["hotel sale delay", "potential loss of BADR", "estate planning gaps"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Confirm BADR eligibility and check for legislative changes",
                deadline=date(2026, 2, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 21)
            ),
            FollowUp(
                commitment="Prepare updated wills recommendation - current from 1995",
                deadline=date(2026, 2, 28),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 21)
            ),
            FollowUp(
                commitment="LPA recommendation and process",
                deadline=date(2026, 2, 28),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 21)
            ),
            FollowUp(
                commitment="Spain residency tax implications research",
                deadline=date(2026, 3, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2026, 1, 21)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2026, 1, 21, 10, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="January review - hotel sale strategy, BADR, wills/LPAs",
                duration_minutes=45,
                next_action="BADR eligibility check"
            ),
            Interaction(
                interaction_date=datetime(2026, 1, 17, 14, 0),
                method=ContactMethod.EMAIL,
                direction="outbound",
                summary="Agent update - pricing guidance unchanged at £1.2-1.3M",
                duration_minutes=0
            ),
            Interaction(
                interaction_date=datetime(2026, 1, 12, 11, 0),
                method=ContactMethod.PHONE,
                direction="inbound",
                summary="Sybil call - renewed frustration over delayed sale. Wants to exit regardless of price.",
                duration_minutes=20,
                next_action="Discuss with Basil"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2026, 1, 21),
            next_review_due=date(2027, 2, 18),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2026, 1, 21),
            value_delivered=[]
        ),
        client_since=date(2019, 6, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["business-exit", "cgt-planning", "cross-border", "estate-planning"],
        notes="Basil highly ego-attached to hotel as life's work. Sybil pragmatic, fatigued, focused on quality of life. No children reduces need to retain UK base. Basil responds best to authoritative data and tax clarity. BADR framing likely key lever to unlock decision."
    )


def create_james_rebecca_martinez() -> Client:
    """
    James & Rebecca Martinez - Dual income tech/NHS, young family,
    house extension plans, pension consolidation opportunity
    """
    return Client(
        id="CLT-2024006",
        title="Mr",
        first_name="James",
        last_name="Martinez",
        date_of_birth=date(1982, 10, 3),
        national_insurance="EF234567E",
        occupation="Software Engineering Manager",
        employer="TechFlow Solutions Ltd",
        annual_income=107000,  # Including bonus and share options
        contact_info=ContactInfo(
            email="james.martinez@techflow.com",
            phone="01483 123456",
            mobile="07845 123987",
            address=Address(
                line1="12 Oakwood Drive",
                city="Godalming",
                county="Surrey",
                postcode="GU7 2BB"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Evening"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Rebecca",
                relationship="spouse",
                date_of_birth=date(1984, 2, 15),
                notes="NHS Consultant Radiologist, Royal Surrey. 4 days/week (0.8 FTE), £98k. Additional private work £6k/year. Wants option to reduce to 3 days from age 50."
            ),
            FamilyMember(
                name="Isabella",
                relationship="child",
                date_of_birth=date(2015, 5, 22),
                notes="Age 9, Godalming Primary School"
            ),
            FamilyMember(
                name="Lucas",
                relationship="child",
                date_of_birth=date(2017, 11, 11),
                notes="Age 6, Godalming Primary School"
            ),
            FamilyMember(
                name="Sofia",
                relationship="child",
                date_of_birth=date(2020, 3, 8),
                notes="Age 4, starting reception September 2024. Nursery fees ending = £400/month saving."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2024, 9, 1),
                description="Sofia starting school - nursery fees (£400/month) ceased, freeing £4,800/year",
                related_person="Sofia",
                source="fact_find"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2027, 6, 1),
                description="House extension planned - extra bedroom and larger kitchen, £80,000 budget",
                source="goals"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 12, 1),
                description="Annual trip to Spain to visit James's father and extended family",
                source="fact_find"
            ),
            LifeEvent(
                event_type=LifeEventType.BIRTHDAY,
                event_date=date(2034, 2, 15),
                description="Rebecca turns 50 - wants option to reduce to 3 days/week",
                related_person="Rebecca",
                source="goals"
            )
        ],
        concerns=[
            Concern(
                topic="emergency fund",
                details="Current savings £12,600 - target 6 months expenses (£30,000). Priority 1 objective.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 9, 8),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 9, 8)
            ),
            Concern(
                topic="pension consolidation",
                details="James has pensions scattered across 3 providers: current SIPP £142,600, previous 1 £34,800, previous 2 £18,200. Total £195,600. Consolidation opportunity.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 9, 8),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 9, 8)
            ),
            Concern(
                topic="Rebecca part-time transition",
                details="Rebecca wants option to reduce to 3 days/week from age 50 (2034). Need to plan for reduced income.",
                severity=ConcernSeverity.LOW,
                date_raised=date(2024, 9, 8),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2024, 9, 8)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Fidelity",
                policy_number="SIPP-FID-JM",
                current_value=142600,
                monthly_contribution=750,
                notes="Current employer scheme. 8% employee + 10% employer."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Scottish Widows",
                policy_number="PP-SW-JM-OLD1",
                current_value=34800,
                monthly_contribution=0,
                notes="Previous employer - consolidation candidate"
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Aegon",
                policy_number="PP-AE-JM-OLD2",
                current_value=18200,
                monthly_contribution=0,
                notes="Previous employer - consolidation candidate"
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="NHS Pension Scheme",
                policy_number="NHS-DB-RM",
                current_value=195200,  # Accrued value estimate
                monthly_contribution=0,
                notes="Rebecca's Defined Benefit. Extremely valuable - do not transfer."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="ISA-VG-JM",
                current_value=28450,
                monthly_contribution=500
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Hargreaves Lansdown",
                policy_number="ISA-HL-RM",
                current_value=31280,
                monthly_contribution=400
            )
        ],
        total_portfolio_value=642730,  # Net worth
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.MEDIUM,
            investment_experience="moderate",
            time_horizon_years=18,  # To age 60
            last_assessed=date(2024, 9, 8),
            notes="Both non-smokers, very active (James triathlon training, Rebecca yoga/swimming). Long time horizon to retirement."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2024, 9, 8),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=90,
                summary="Initial fact-find. Dual-income tech/NHS couple with 3 young children. Strong position but emergency fund below target. James has scattered pensions - consolidation opportunity. Sofia starting school frees £400/month.",
                key_points=[
                    "Combined income £211k gross, £11,500 net monthly",
                    "Monthly surplus £2,209 after Sofia school frees £400",
                    "Emergency fund £12.6k - target £30k",
                    "James pension consolidation opportunity (3 providers)",
                    "Rebecca NHS DB extremely valuable - retain",
                    "House extension £80k planned in 2-3 years"
                ],
                action_items=[
                    "Build emergency fund to £30k",
                    "James pension consolidation review",
                    "Review protection levels",
                    "House extension funding strategy"
                ],
                concerns_raised=["emergency fund", "pension consolidation"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Prepare pension consolidation recommendation for James (3 schemes → 1)",
                deadline=date(2024, 10, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2024, 9, 8)
            ),
            FollowUp(
                commitment="Protection review - check current levels adequate for 3 children",
                deadline=date(2024, 10, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2024, 9, 8)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2024, 9, 8, 19, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Initial fact-find meeting. Comprehensive review of finances, goals, concerns.",
                duration_minutes=90,
                next_action="Pension consolidation analysis"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=None,
            next_review_due=date(2025, 9, 8),
            review_status="pending",
            suitability_confirmed=False,
            value_delivered=[]
        ),
        client_since=date(2024, 9, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["young-family", "pension-consolidation", "dual-income", "nhs-db"],
        notes="James: British/Spanish dual nationality (Spanish father). Speaks fluent Spanish. Very active - triathlon training. Annual trips to Spain to visit family. Rebecca NHS consultant, considering part-time at 50."
    )


def create_anne_partridge() -> Client:
    """
    Anne Partridge - Widow, recently bereaved, inherited pension,
    needs careful emotional handling, estate planning
    """
    return Client(
        id="CLT-2024020",
        title="Mrs",
        first_name="Anne",
        last_name="Partridge",
        date_of_birth=date(1956, 11, 23),
        occupation="Retired Teacher",
        employer=None,
        annual_income=35000,  # Pension income
        contact_info=ContactInfo(
            email="anne.partridge@btinternet.com",
            phone="01onal 234567",
            mobile="07734 567890",
            address=Address(
                line1="14 Rose Cottage Lane",
                city="Henley-on-Thames",
                county="Oxfordshire",
                postcode="RG9 2AB"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Afternoon"
        ),
        marital_status="widowed",
        family_members=[
            FamilyMember(
                name="Richard (deceased)",
                relationship="spouse",
                date_of_birth=date(1954, 3, 8),
                notes="Passed away October 2025 after long illness. Was a chartered accountant. Anne now managing finances alone for first time."
            ),
            FamilyMember(
                name="Catherine",
                relationship="child",
                date_of_birth=date(1985, 7, 14),
                notes="Age 39, lives in Bristol with husband and 2 children. Close relationship with Anne."
            ),
            FamilyMember(
                name="William",
                relationship="child",
                date_of_birth=date(1988, 12, 3),
                notes="Age 36, lives in Edinburgh. Works in finance."
            ),
            FamilyMember(
                name="Emily",
                relationship="grandchild",
                date_of_birth=date(2018, 4, 12),
                notes="Catherine's daughter, age 6"
            ),
            FamilyMember(
                name="Thomas",
                relationship="grandchild",
                date_of_birth=date(2021, 9, 28),
                notes="Catherine's son, age 3"
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.DEATH_IN_FAMILY,
                event_date=date(2025, 10, 15),
                description="Richard passed away after long illness. Anne now managing finances alone for first time in 45 years of marriage.",
                related_person="Richard",
                source="bereavement_meeting"
            ),
            LifeEvent(
                event_type=LifeEventType.BIRTHDAY,
                event_date=date(2026, 11, 23),
                description="Anne's 70th birthday - first significant birthday without Richard",
                source="client_data"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 4, 12),
                description="Granddaughter Emily's 8th birthday",
                related_person="Emily",
                source="family_data"
            )
        ],
        concerns=[
            Concern(
                topic="managing finances alone",
                details="Richard always handled investments and financial decisions during 45-year marriage. Anne has never managed money alone. Feeling overwhelmed and anxious about making wrong decisions.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 11, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 11, 20),
                notes="Needs patient, clear explanations. Don't rush decisions."
            ),
            Concern(
                topic="inheritance for grandchildren",
                details="Wants to ensure grandchildren (Emily 6, Thomas 3) benefit from estate. Considering gifts now vs waiting. Worried about IHT.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 11, 20),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 11, 20)
            ),
            Concern(
                topic="income sustainability",
                details="Concerned whether inherited investments plus pensions will last. Doesn't want to burden children. Very frugal mindset.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 11, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 11, 20)
            ),
            Concern(
                topic="loneliness and isolation",
                details="Large family home now feels empty. Mentioned staying for memories but house is expensive to run. Children encouraging downsizing but emotionally difficult.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 11, 20),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 11, 20),
                notes="Non-financial but affects decision-making. Be sensitive."
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Teachers' Pension Scheme",
                policy_number="TPS-DB-AP",
                current_value=0,  # DB
                monthly_contribution=0,
                notes="Defined Benefit. £18,000/year index-linked. Widow's portion of Richard's pension adds £8,000/year."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Hargreaves Lansdown",
                policy_number="SIPP-HL-RP-INHERITED",
                current_value=340000,
                monthly_contribution=0,
                notes="Inherited from Richard. Needs review - currently in cash after transfer. Income drawdown to set up."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="ISA-VG-AP",
                current_value=85000,
                monthly_contribution=0,
                notes="Inherited from Richard. Conservative allocation needed for Anne's risk profile."
            )
        ],
        total_portfolio_value=750000,  # Including house equity
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.LOW,
            capacity_for_loss=RiskAttitude.MEDIUM,
            investment_experience="limited",
            time_horizon_years=15,
            last_assessed=date(2025, 11, 20),
            notes="Very cautious. Richard handled all investments. Needs simple explanations and reassurance. Don't recommend complex products."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 11, 20),
                meeting_type=ContactMethod.IN_PERSON,
                duration_minutes=90,
                summary="First meeting since Richard's passing. Anne emotional but coping. Overwhelmed by financial decisions. Inherited SIPP sitting in cash. Teachers pension plus widow's portion provides solid base. Main concern is making wrong decisions without Richard.",
                key_points=[
                    "Richard passed October 2025 after long illness",
                    "Anne never managed finances in 45-year marriage",
                    "Inherited SIPP £340k sitting in cash - needs investment",
                    "Teachers pension £18k + widow's pension £8k = £26k guaranteed",
                    "Concerned about grandchildren inheritance",
                    "Large house expensive to run but emotionally attached"
                ],
                action_items=[
                    "Simple investment proposal for inherited SIPP",
                    "Income projection to show sustainability",
                    "Estate planning review",
                    "Gentle discussion about downsizing options (not rushing)"
                ],
                concerns_raised=["managing finances alone", "inheritance for grandchildren", "income sustainability"],
                life_events_mentioned=["Richard passed away", "Anne's 70th birthday coming"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Prepare simple investment proposal for inherited SIPP - low risk, income focus",
                deadline=date(2025, 12, 10),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 11, 20),
                notes="Keep it simple - she's overwhelmed. Maximum 3 fund options."
            ),
            FollowUp(
                commitment="Create income sustainability projection to reassure about long-term security",
                deadline=date(2025, 12, 10),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 11, 20)
            ),
            FollowUp(
                commitment="Phone call to check in - how is she coping?",
                deadline=date(2025, 12, 1),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 11, 20),
                notes="Welfare check, not business. Be human."
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 11, 20, 14, 0),
                method=ContactMethod.IN_PERSON,
                direction="outbound",
                summary="First meeting post-bereavement. Home visit to Anne. Emotional but coping. Discussed inherited SIPP, income needs, grandchildren.",
                duration_minutes=90,
                next_action="Prepare simple investment proposal"
            ),
            Interaction(
                interaction_date=datetime(2025, 11, 1, 10, 30),
                method=ContactMethod.PHONE,
                direction="inbound",
                summary="Catherine (daughter) called on behalf of Anne to notify of Richard's passing and ask for help with finances.",
                duration_minutes=20,
                next_action="Schedule home visit"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=None,
            next_review_due=date(2026, 11, 20),
            review_status="pending",
            suitability_confirmed=False,
            value_delivered=[],
            notes="Bereaved client - handle with extra care. Don't rush decisions."
        ),
        client_since=date(2018, 6, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["bereaved", "inherited-pension", "low-risk", "needs-support"],
        notes="Recently widowed after 45-year marriage. Never managed money alone. Needs patient, clear explanations. Don't recommend complex products. Check in regularly - welfare as important as financial advice. Catherine (daughter) helpful point of contact if needed."
    )


def create_priya_raj_patel() -> Client:
    """
    Priya & Raj Patel - Small business owners, commercial property,
    pension contributions optimization, adult children
    """
    return Client(
        id="CLT-2024008",
        title="Mrs",
        first_name="Priya",
        last_name="Patel",
        date_of_birth=date(1968, 8, 15),
        occupation="Pharmacist/Business Owner",
        employer="Patel Family Pharmacy Ltd",
        annual_income=95000,
        contact_info=ContactInfo(
            email="priya.patel@patelfamilypharmacy.co.uk",
            phone="0161 234 5678",
            mobile="07890 123456",
            address=Address(
                line1="28 Victoria Gardens",
                city="Altrincham",
                county="Greater Manchester",
                postcode="WA14 2PL"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Afternoon"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Raj",
                relationship="spouse",
                date_of_birth=date(1965, 4, 22),
                notes="Age 59. Co-owner Patel Family Pharmacy. £95k income. Wants to retire at 62. Health good but starting to feel tired."
            ),
            FamilyMember(
                name="Anita",
                relationship="child",
                date_of_birth=date(1995, 3, 10),
                notes="Age 29. Qualified pharmacist. Works in the family business. May take over when parents retire."
            ),
            FamilyMember(
                name="Sanjay",
                relationship="child",
                date_of_birth=date(1998, 11, 28),
                notes="Age 26. Software developer in London. Not interested in family business."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.WEDDING,
                event_date=date(2026, 8, 15),
                description="Anita's wedding planned for August 2026. Parents contributing £50k.",
                related_person="Anita",
                source="meeting_notes"
            ),
            LifeEvent(
                event_type=LifeEventType.RETIREMENT,
                event_date=date(2027, 4, 22),
                description="Raj target retirement at 62. Priya may continue part-time.",
                related_person="Raj",
                source="planning"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2027, 6, 1),
                description="Business succession - Anita potentially taking over pharmacy",
                related_person="Anita",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="business succession planning",
                details="Anita may take over pharmacy when parents retire. Need to plan transition - timing, valuation, tax efficiency. Sanjay not interested but should be treated fairly in estate.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 1)
            ),
            Concern(
                topic="pension contributions optimization",
                details="Both have significant pension headroom. Combined income £190k. Could maximize contributions for tax efficiency. Carry forward available.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 1)
            ),
            Concern(
                topic="commercial property in pension",
                details="Own pharmacy premises personally. Discussed transferring to SIPP - CGT, SDLT implications. Would provide tax-free rental income to pension.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 6, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 12, 1),
                notes="Complex transaction - needs specialist input"
            ),
            Concern(
                topic="Anita's wedding costs",
                details="Contributing £50k to Anita's wedding August 2026. Impacts cash reserves and investment timing.",
                severity=ConcernSeverity.LOW,
                date_raised=date(2025, 12, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 1)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="AJ Bell",
                policy_number="SIPP-AJB-PP",
                current_value=420000,
                monthly_contribution=3000,
                notes="Priya's SIPP. Maximizing contributions for tax efficiency."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="AJ Bell",
                policy_number="SIPP-AJB-RP",
                current_value=385000,
                monthly_contribution=3500,
                notes="Raj's SIPP. Maximizing contributions, especially with retirement at 62 target."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Hargreaves Lansdown",
                policy_number="ISA-HL-JOINT",
                current_value=180000,
                monthly_contribution=1666,
                notes="Joint ISAs, both maximizing allowances"
            ),
            Policy(
                policy_type=PolicyType.LIFE_INSURANCE,
                provider="Legal & General",
                policy_number="LIFE-LG-PP",
                current_value=500000,
                monthly_contribution=65,
                notes="Joint life first death. In trust for children."
            )
        ],
        total_portfolio_value=1850000,  # Including commercial property and business value
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="moderate",
            time_horizon_years=8,
            last_assessed=date(2025, 6, 1),
            notes="Business owners understand risk. Want diversification away from business. Raj becoming more conservative as retirement approaches."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 12, 1),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=60,
                summary="Annual review. Anita's wedding August 2026 - £50k contribution confirmed. Raj increasingly talking about retirement at 62 (April 2027). Business succession with Anita progressing - she's now dispensary manager.",
                key_points=[
                    "Anita's wedding August 2026 - £50k contribution",
                    "Raj retirement target April 2027 (age 62)",
                    "Anita now dispensary manager - succession progressing",
                    "Sanjay not interested in business but needs fair treatment",
                    "Commercial property to SIPP still under consideration",
                    "Pension contributions maximized for tax efficiency"
                ],
                action_items=[
                    "Wedding gift planning - timing and method",
                    "Update retirement projection with 2027 target",
                    "Business valuation for succession planning",
                    "Review commercial property to SIPP feasibility"
                ],
                concerns_raised=["business succession planning", "Anita's wedding costs"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Coordinate with accountant on business valuation for succession",
                deadline=date(2026, 2, 1),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 12, 1)
            ),
            FollowUp(
                commitment="Update retirement projection with Raj at 62 scenario",
                deadline=date(2026, 1, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 12, 1)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 12, 1, 16, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Annual review - wedding planning, retirement timeline, succession",
                duration_minutes=60,
                next_action="Business valuation coordination"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 12, 1),
            next_review_due=date(2026, 12, 1),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 12, 1),
            value_delivered=[
                "Pension contribution optimization - saves £15k tax annually",
                "Business succession planning initiated",
                "Protection review completed"
            ]
        ),
        client_since=date(2019, 3, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["business-owner", "succession-planning", "high-value", "pension-optimization"],
        notes="Family pharmacy business established 1992. Community focused. Strong family values. Anita likely successor. Sanjay in London - needs fair treatment in estate despite not taking business."
    )


def create_rodney_cassandra_trotter() -> Client:
    """
    Rodney & Cassandra Trotter - Self-employed trader, variable income,
    first home buyers, young married couple
    """
    return Client(
        id="CLT-2024010",
        title="Mr",
        first_name="Rodney",
        last_name="Trotter",
        date_of_birth=date(1985, 2, 28),
        national_insurance="GH567890G",
        occupation="Self-Employed Trader",
        employer="Trotters Independent Traders",
        annual_income=48000,
        contact_info=ContactInfo(
            email="rodney.trotter@titco.co.uk",
            phone="020 7946 0958",
            mobile="07700 123456",
            address=Address(
                line1="Flat 12, Nelson Mandela House",
                line2="Peckham High Street",
                city="London",
                county="Greater London",
                postcode="SE15 5DQ"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Afternoon"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Cassandra",
                relationship="spouse",
                date_of_birth=date(1988, 5, 15),
                notes="Bank manager at Lloyds, £52k salary. Very financially savvy. Often helps Rodney with money decisions."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 6, 1),
                description="Looking to buy first home - £350k budget, saving for deposit",
                source="meeting_notes"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2027, 1, 1),
                description="Planning to start a family - Cassandra wants to take maternity leave",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="variable income",
                details="Self-employed income varies significantly month to month. Difficult to plan and save consistently. Cassandra's salary provides stability.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 9, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 15)
            ),
            Concern(
                topic="house deposit savings",
                details="Need £35k deposit for £350k property. Currently have £22k saved. Target completion by June 2026.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 9, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 15)
            ),
            Concern(
                topic="inadequate life insurance",
                details="No life insurance currently. With mortgage and potential family, protection review needed.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 12, 15),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 12, 15)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.ISA,
                provider="Moneybox",
                policy_number="ISA-MB-RT",
                current_value=22000,
                monthly_contribution=800,
                notes="Lifetime ISA for house deposit. £4k annual limit. 25% government bonus."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Nest",
                policy_number="NEST-RT",
                current_value=18500,
                monthly_contribution=200,
                notes="Self-employed pension. Considering increasing contributions."
            )
        ],
        total_portfolio_value=45000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.LOW,
            investment_experience="limited",
            time_horizon_years=25,
            last_assessed=date(2025, 9, 1),
            notes="Cassandra more financially literate than Rodney. Both understand need for protection."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 12, 15),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=45,
                summary="Review of house deposit progress. £22k saved, need £35k by June 2026. Discussed protection gap.",
                key_points=[
                    "House deposit £22k, target £35k by June 2026",
                    "Cassandra's salary provides income stability",
                    "No life insurance - needs addressing before mortgage",
                    "Family planning 2027 - maternity planning needed"
                ],
                action_items=[
                    "Life insurance quotes for both",
                    "Mortgage affordability projection"
                ],
                concerns_raised=["house deposit savings", "inadequate life insurance"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Obtain life insurance quotes for Rodney and Cassandra",
                deadline=date(2026, 1, 31),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 12, 15)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 12, 15, 18, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="House deposit review and protection discussion",
                duration_minutes=45,
                next_action="Life insurance quotes"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 9, 1),
            next_review_due=date(2026, 9, 1),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 9, 1)
        ),
        client_since=date(2024, 6, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["first-time-buyer", "young-couple", "self-employed"],
        notes="Rodney has older brother Derek who handles most of business. Cassandra very sensible, often takes lead in financial discussions."
    )


def create_hyacinth_richard_bucket() -> Client:
    """
    Hyacinth & Richard Bucket - Retired, status-conscious,
    wants to leave inheritance, concerned about care costs
    """
    return Client(
        id="CLT-2024011",
        title="Mrs",
        first_name="Hyacinth",
        last_name="Bucket",
        date_of_birth=date(1952, 4, 10),
        occupation="Retired",
        employer=None,
        annual_income=42000,  # Pension income
        contact_info=ContactInfo(
            email="hyacinth.bucket@btinternet.com",
            phone="01onal 789012",
            mobile="07890 111222",
            address=Address(
                line1="The Old Vicarage",
                line2="Blossom Avenue",
                city="Royal Leamington Spa",
                county="Warwickshire",
                postcode="CV32 5BP"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Morning"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Richard",
                relationship="spouse",
                date_of_birth=date(1950, 8, 20),
                notes="Age 75. Retired council worker. Very easy-going. Health good but had minor heart procedure 2024."
            ),
            FamilyMember(
                name="Sheridan",
                relationship="child",
                date_of_birth=date(1980, 6, 15),
                notes="Age 45. Lives in London. Unmarried. Works in 'the arts'. Hyacinth very proud of him."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.BIRTHDAY,
                event_date=date(2026, 4, 10),
                description="Hyacinth's 74th birthday - planning 'intimate garden party for 200 guests'",
                source="client_mentioned"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 8, 1),
                description="Richard's 76th birthday - Hyacinth planning cruise to celebrate",
                related_person="Richard",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="care home costs",
                details="Very worried about potential care costs eroding estate. Wants to protect assets for Sheridan. Discussed gifting but concerned about 7-year rule.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 10, 15),
                notes="Hyacinth adamant about not 'ending up in one of those places'. Premium care only if needed."
            ),
            Concern(
                topic="inheritance tax",
                details="Estate estimated £1.2M including house. Wants to minimize IHT for Sheridan. Currently £280k above nil-rate bands.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 10, 15)
            ),
            Concern(
                topic="Richard's health",
                details="Had minor heart procedure in 2024. Now stable but Hyacinth anxious about future.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 11, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 10, 15)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="LGPS",
                policy_number="LGPS-RB-DB",
                current_value=0,
                monthly_contribution=0,
                notes="Richard's DB pension. £18k/year index-linked. 50% survivor benefit."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Prudential",
                policy_number="PP-PRU-HB",
                current_value=145000,
                monthly_contribution=0,
                notes="Hyacinth's personal pension from brief office career."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Hargreaves Lansdown",
                policy_number="ISA-HL-BUCKET",
                current_value=185000,
                monthly_contribution=0,
                notes="Joint ISAs built over years. Conservative allocation."
            )
        ],
        total_portfolio_value=1200000,  # Including house
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.LOW,
            capacity_for_loss=RiskAttitude.MEDIUM,
            investment_experience="limited",
            time_horizon_years=10,
            last_assessed=date(2025, 6, 1),
            notes="Very conservative. Hyacinth makes all decisions. Richard agrees with everything."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 10, 15),
                meeting_type=ContactMethod.IN_PERSON,
                duration_minutes=75,
                summary="Annual review at their home. Hyacinth served 'light refreshments' (5 course meal). Main focus on IHT planning and care cost concerns.",
                key_points=[
                    "Estate £1.2M - £280k above nil-rate bands",
                    "Care costs major worry - want to protect for Sheridan",
                    "Discussed gifting strategy but 7-year rule concern",
                    "Richard health stable post-procedure",
                    "Cruise planned for Richard's 76th"
                ],
                action_items=[
                    "Care fees planning meeting with specialist",
                    "Review gifting strategy",
                    "Update wills"
                ],
                concerns_raised=["care home costs", "inheritance tax"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Arrange care fees planning meeting",
                deadline=date(2025, 12, 1),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2025, 10, 15)
            ),
            FollowUp(
                commitment="Review gifting strategy options",
                deadline=date(2025, 12, 15),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2025, 10, 15)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 10, 15, 10, 30),
                method=ContactMethod.IN_PERSON,
                direction="outbound",
                summary="Annual review at home. IHT and care planning.",
                duration_minutes=75,
                next_action="Care fees meeting"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 10, 15),
            next_review_due=date(2026, 10, 15),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 10, 15)
        ),
        client_since=date(2015, 4, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["retiree", "estate-planning", "care-planning", "high-maintenance"],
        notes="Hyacinth pronounces it 'Bouquet'. Very particular about everything. Meetings always involve elaborate hospitality. Good clients but require careful handling of expectations. Richard very easy-going."
    )


def create_keith_candice_lard() -> Client:
    """
    Keith & Candice Lard - Public sector workers, NHS and council,
    solid DB pensions, straightforward planning needs
    """
    return Client(
        id="CLT-2024012",
        title="Mr",
        first_name="Keith",
        last_name="Lard",
        date_of_birth=date(1972, 11, 5),
        occupation="Health & Safety Manager",
        employer="Bolton Metropolitan Borough Council",
        annual_income=52000,
        contact_info=ContactInfo(
            email="keith.lard@gmail.com",
            phone="01204 123456",
            mobile="07456 789012",
            address=Address(
                line1="42 Coronation Street",
                city="Bolton",
                county="Greater Manchester",
                postcode="BL1 4QP"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Evening"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="Candice",
                relationship="spouse",
                date_of_birth=date(1975, 3, 22),
                notes="NHS Band 6 Nurse, £45k. Works at Royal Bolton Hospital. 20 years NHS service."
            ),
            FamilyMember(
                name="Darren",
                relationship="child",
                date_of_birth=date(2002, 7, 14),
                notes="Age 23. Graduated 2024. Working as junior accountant."
            ),
            FamilyMember(
                name="Kelly",
                relationship="child",
                date_of_birth=date(2005, 4, 30),
                notes="Age 20. At University of Manchester, second year Business Studies."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.RETIREMENT,
                event_date=date(2032, 11, 5),
                description="Keith target retirement at 60. Strong LGPS pension.",
                source="planning"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2027, 6, 1),
                description="Kelly university graduation expected",
                related_person="Kelly",
                source="family_timeline"
            )
        ],
        concerns=[
            Concern(
                topic="retirement income adequacy",
                details="Both have DB pensions but want to ensure combined income meets target £45k/year.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 3, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 11, 1)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="LGPS",
                policy_number="LGPS-KL-DB",
                current_value=0,
                monthly_contribution=0,
                notes="Keith's LGPS. 25 years service. Projected £22k/year at 60."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="NHS Pension Scheme",
                policy_number="NHS-CL-DB",
                current_value=0,
                monthly_contribution=0,
                notes="Candice's NHS pension. 20 years service. Projected £18k/year at 60."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Halifax",
                policy_number="ISA-HFX-LARD",
                current_value=45000,
                monthly_contribution=500,
                notes="Joint ISAs. Targeting extra retirement pot."
            )
        ],
        total_portfolio_value=320000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.MEDIUM,
            investment_experience="limited",
            time_horizon_years=7,
            last_assessed=date(2025, 3, 1),
            notes="Both understand pensions well due to public sector experience."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 11, 1),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=45,
                summary="Annual review. Retirement projections on track. ISA contributions maintained.",
                key_points=[
                    "Combined DB pensions project £40k/year",
                    "ISA pot adds flexibility",
                    "Kelly at university - supporting with living costs",
                    "Darren now employed and self-sufficient"
                ],
                action_items=[
                    "Update pension projections"
                ],
                concerns_raised=["retirement income adequacy"]
            )
        ],
        follow_ups=[],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 11, 1, 19, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Annual review",
                duration_minutes=45,
                next_action="None immediate"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 11, 1),
            next_review_due=date(2026, 11, 1),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 11, 1)
        ),
        client_since=date(2020, 3, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["public-sector", "db-pension", "straightforward"],
        notes="Very straightforward clients. Both understand their pensions well. Annual review is mainly reassurance."
    )


def create_gareth_cheeseman() -> Client:
    """
    Gareth Cheeseman - Single, sales executive, high earner,
    bonus-driven, lacks pension planning focus
    """
    return Client(
        id="CLT-2024013",
        title="Mr",
        first_name="Gareth",
        last_name="Cheeseman",
        date_of_birth=date(1978, 9, 18),
        occupation="Regional Sales Director",
        employer="Infinidium Solutions Ltd",
        annual_income=125000,
        contact_info=ContactInfo(
            email="gareth.cheeseman@infinidium.com",
            phone="0118 496 0999",
            mobile="07911 234567",
            address=Address(
                line1="Penthouse Suite, The Cube",
                city="Reading",
                county="Berkshire",
                postcode="RG1 2BN"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Anytime"
        ),
        marital_status="single",
        family_members=[],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 3, 15),
                description="Expected bonus £45k - needs tax-efficient deployment",
                source="client_mentioned"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 7, 1),
                description="Considering property purchase - buy-to-let investment",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="tax efficiency",
                details="High earner losing personal allowance. Bonus comes in lump sum. Needs tax planning.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 10, 1)
            ),
            Concern(
                topic="pension underfunding",
                details="Only £85k in pension at 47. Late starter. Needs to maximize contributions. Carry-forward available.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 10, 1)
            ),
            Concern(
                topic="no protection",
                details="No life insurance, CI, or income protection. Single but valuable employee. Company scheme only.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 10, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 10, 1)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Aviva",
                policy_number="SIPP-AV-GC",
                current_value=85000,
                monthly_contribution=1500,
                notes="Recently increased from £500/month. Carry-forward being used."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Interactive Investor",
                policy_number="ISA-II-GC",
                current_value=62000,
                monthly_contribution=1000,
                notes="Aggressive growth portfolio. 90% equities."
            )
        ],
        total_portfolio_value=285000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.HIGH,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="moderate",
            time_horizon_years=18,
            last_assessed=date(2025, 10, 1),
            notes="High risk tolerance. Wants growth. Understands volatility."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 10, 1),
                meeting_type=ContactMethod.IN_PERSON,
                duration_minutes=60,
                summary="Initial comprehensive meeting. High earner with tax issues and pension underfunding. Bonus due March 2026 needs planning.",
                key_points=[
                    "Income £125k + £45k expected bonus",
                    "Losing personal allowance - 60% marginal rate",
                    "Pension only £85k at 47 - late starter",
                    "No protection in place",
                    "Interested in buy-to-let"
                ],
                action_items=[
                    "Bonus tax planning strategy",
                    "Pension catch-up using carry-forward",
                    "Protection review"
                ],
                concerns_raised=["tax efficiency", "pension underfunding", "no protection"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Prepare bonus tax planning strategy for March 2026",
                deadline=date(2026, 2, 1),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 10, 1)
            ),
            FollowUp(
                commitment="Protection quotes (life, CI, IP)",
                deadline=date(2025, 11, 15),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2025, 10, 1)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 10, 1, 12, 0),
                method=ContactMethod.IN_PERSON,
                direction="outbound",
                summary="Initial comprehensive review",
                duration_minutes=60,
                next_action="Tax planning strategy"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 10, 1),
            next_review_due=date(2026, 10, 1),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 10, 1)
        ),
        client_since=date(2025, 9, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["high-earner", "tax-planning", "pension-catch-up", "single"],
        notes="Very confident personality. Likes to think he knows about investments. Needs to be carefully guided. Late to pension saving but income allows aggressive catch-up."
    )


def create_lisa_rahman() -> Client:
    """
    Lisa Rahman - Single mum, NHS worker, modest income,
    focused on children's future, needs protection review
    """
    return Client(
        id="CLT-2024014",
        title="Ms",
        first_name="Lisa",
        last_name="Rahman",
        date_of_birth=date(1982, 6, 25),
        occupation="NHS Administrator",
        employer="Birmingham Women's Hospital",
        annual_income=32000,
        contact_info=ContactInfo(
            email="lisa.rahman@nhs.net",
            phone="0121 234 5678",
            mobile="07789 345678",
            address=Address(
                line1="28 Maple Road",
                city="Birmingham",
                county="West Midlands",
                postcode="B29 6PQ"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Lunchtime"
        ),
        marital_status="divorced",
        family_members=[
            FamilyMember(
                name="Aisha",
                relationship="child",
                date_of_birth=date(2014, 3, 12),
                notes="Age 11. Very bright. Lisa wants to save for university."
            ),
            FamilyMember(
                name="Omar",
                relationship="child",
                date_of_birth=date(2016, 11, 8),
                notes="Age 9. Into football. Lisa managing costs of activities."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.BIRTHDAY,
                event_date=date(2026, 3, 12),
                description="Aisha's 12th birthday",
                related_person="Aisha",
                source="family_data"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2032, 9, 1),
                description="Aisha university start - 6 years to save",
                related_person="Aisha",
                source="planning"
            )
        ],
        concerns=[
            Concern(
                topic="children's education funding",
                details="Wants to save for Aisha and Omar's university. Limited monthly surplus. JISAs started but contributions modest.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 9, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 9, 15)
            ),
            Concern(
                topic="protection as single parent",
                details="Critical that children are provided for if Lisa becomes ill or dies. Current life cover £100k may be insufficient.",
                severity=ConcernSeverity.HIGH,
                date_raised=date(2024, 9, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 9, 15)
            ),
            Concern(
                topic="pension at divorce",
                details="Pension sharing order from divorce gave Lisa additional CETV but she's unsure how to manage it.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 9, 1),
                status=ConcernStatus.MONITORING,
                last_discussed=date(2025, 9, 15)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="NHS Pension Scheme",
                policy_number="NHS-LR-DB",
                current_value=0,
                monthly_contribution=0,
                notes="Lisa's NHS DB pension. 12 years service."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Scottish Widows",
                policy_number="CETV-SW-LR",
                current_value=48000,
                monthly_contribution=0,
                notes="CETV from divorce settlement. Needs investment strategy."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="JISA-VG-AISHA",
                current_value=4200,
                monthly_contribution=50,
                notes="Aisha's Junior ISA"
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Vanguard",
                policy_number="JISA-VG-OMAR",
                current_value=2800,
                monthly_contribution=50,
                notes="Omar's Junior ISA"
            ),
            Policy(
                policy_type=PolicyType.LIFE_INSURANCE,
                provider="Legal & General",
                policy_number="LIFE-LG-LR",
                current_value=100000,
                monthly_contribution=18,
                renewal_date=date(2035, 1, 1),
                notes="Level term. May need increasing."
            )
        ],
        total_portfolio_value=78000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.LOW,
            investment_experience="limited",
            time_horizon_years=20,
            last_assessed=date(2024, 9, 1),
            notes="Limited capacity for loss due to single-income household."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 9, 15),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=40,
                summary="Annual review. Discussed protection adequacy and children's savings. Lisa managing well on limited budget.",
                key_points=[
                    "Life cover £100k - may need review with children older",
                    "JISAs ongoing at £50 each",
                    "CETV needs investment strategy",
                    "NHS pension building well"
                ],
                action_items=[
                    "Protection review and quote",
                    "CETV investment recommendation"
                ],
                concerns_raised=["protection as single parent", "children's education funding"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Protection review and increased cover quote",
                deadline=date(2025, 10, 31),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2025, 9, 15)
            ),
            FollowUp(
                commitment="CETV investment strategy recommendation",
                deadline=date(2025, 11, 30),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2025, 9, 15)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 9, 15, 12, 30),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Annual review - protection and savings",
                duration_minutes=40,
                next_action="Protection review"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 9, 15),
            next_review_due=date(2026, 9, 15),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 9, 15)
        ),
        client_since=date(2024, 6, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["single-parent", "modest-income", "protection-focus", "children-savings"],
        notes="Lisa managing well as single mum. Very focused on children's future. Limited budget but committed to saving. Ex-husband pays child maintenance regularly."
    )


def create_emma_john_thompson() -> Client:
    """
    Emma & John Thompson (no relation to Sarah) - Mid-40s, 
    dormant client, need to re-engage, pension scattered
    """
    return Client(
        id="CLT-2024016",
        title="Mrs",
        first_name="Emma",
        last_name="Williams",
        date_of_birth=date(1979, 12, 3),
        occupation="HR Director",
        employer="Williams & Co Solicitors",
        annual_income=88000,
        contact_info=ContactInfo(
            email="emma.williams@williamsco.com",
            phone="01onal 456789",
            mobile="07890 567890",
            address=Address(
                line1="The Old Rectory",
                city="Winchester",
                county="Hampshire",
                postcode="SO23 8AQ"
            ),
            preferred_contact_method=ContactMethod.EMAIL,
            best_time_to_call="Afternoon"
        ),
        marital_status="married",
        family_members=[
            FamilyMember(
                name="John",
                relationship="spouse",
                date_of_birth=date(1977, 5, 14),
                notes="Solicitor partner at Williams & Co. £145k income."
            ),
            FamilyMember(
                name="Charlotte",
                relationship="child",
                date_of_birth=date(2008, 8, 22),
                notes="Age 17. A-levels 2026."
            ),
            FamilyMember(
                name="Henry",
                relationship="child",
                date_of_birth=date(2011, 2, 15),
                notes="Age 14. GCSEs 2027."
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 8, 1),
                description="Charlotte A-level results and university applications",
                related_person="Charlotte",
                source="family_timeline"
            )
        ],
        concerns=[
            Concern(
                topic="scattered pensions",
                details="Both have multiple pensions from career moves. John has 4 schemes, Emma has 3. Need consolidation review.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2024, 6, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2024, 6, 15)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Various",
                policy_number="MULTIPLE-EW",
                current_value=156000,
                monthly_contribution=600,
                notes="Emma's pensions across 3 providers. Consolidation recommended."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="Various",
                policy_number="MULTIPLE-JW",
                current_value=285000,
                monthly_contribution=1200,
                notes="John's pensions across 4 providers. Consolidation recommended."
            )
        ],
        total_portfolio_value=890000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="moderate",
            time_horizon_years=15,
            last_assessed=date(2024, 6, 1),
            notes="Both professionals, understand investments."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2024, 6, 15),
                meeting_type=ContactMethod.VIDEO_CALL,
                duration_minutes=50,
                summary="Pension consolidation discussion. Both keen to simplify. Agreed to gather pension details.",
                key_points=[
                    "7 pension schemes between them",
                    "Want simplification",
                    "Agreed to send pension statements"
                ],
                action_items=[
                    "Gather all pension statements",
                    "Prepare consolidation recommendation"
                ],
                concerns_raised=["scattered pensions"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Follow up on pension statements",
                deadline=date(2024, 7, 31),
                status=FollowUpStatus.OVERDUE,
                created_date=date(2024, 6, 15),
                notes="Client hasn't responded. Need to chase."
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2024, 6, 15, 15, 0),
                method=ContactMethod.VIDEO_CALL,
                direction="outbound",
                summary="Pension consolidation meeting",
                duration_minutes=50,
                next_action="Await pension statements"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2024, 6, 15),
            next_review_due=date(2025, 6, 15),
            review_status="overdue",
            suitability_confirmed=True,
            suitability_date=date(2024, 6, 15)
        ),
        client_since=date(2022, 3, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["dormant", "re-engage", "pension-consolidation", "high-value"],
        notes="Good clients gone quiet. Need to re-engage. May be busy with work and family. Send friendly re-engagement email."
    )


def create_anthony_makepeace() -> Client:
    """
    Anthony Makepeace - Widower, retired GP, comfortable,
    focused on grandchildren, charity-minded
    """
    return Client(
        id="CLT-2024017",
        title="Dr",
        first_name="Anthony",
        last_name="Makepeace",
        date_of_birth=date(1948, 7, 8),
        occupation="Retired GP",
        employer=None,
        annual_income=65000,  # Pension and investment income
        contact_info=ContactInfo(
            email="dr.makepeace@doctors.org.uk",
            phone="01onal 234567",
            mobile="07700 234567",
            address=Address(
                line1="Orchard House",
                line2="The Green",
                city="Chipping Campden",
                county="Gloucestershire",
                postcode="GL55 6AU"
            ),
            preferred_contact_method=ContactMethod.PHONE,
            best_time_to_call="Morning"
        ),
        marital_status="widowed",
        family_members=[
            FamilyMember(
                name="Margaret (deceased)",
                relationship="spouse",
                date_of_birth=date(1950, 3, 15),
                notes="Passed away 2022 after long illness. Anthony still adjusting."
            ),
            FamilyMember(
                name="Catherine",
                relationship="child",
                date_of_birth=date(1978, 11, 22),
                notes="Age 47. Lives in Oxford. Medical researcher. Married with 2 children."
            ),
            FamilyMember(
                name="James",
                relationship="child",
                date_of_birth=date(1981, 4, 5),
                notes="Age 44. Lives in Edinburgh. Surgeon. Married with 1 child."
            ),
            FamilyMember(
                name="Lily",
                relationship="grandchild",
                date_of_birth=date(2015, 6, 10),
                notes="Catherine's daughter, age 10"
            ),
            FamilyMember(
                name="George",
                relationship="grandchild",
                date_of_birth=date(2018, 12, 3),
                notes="Catherine's son, age 7"
            ),
            FamilyMember(
                name="Beatrice",
                relationship="grandchild",
                date_of_birth=date(2020, 9, 18),
                notes="James's daughter, age 5"
            )
        ],
        life_events=[
            LifeEvent(
                event_type=LifeEventType.BIRTHDAY,
                event_date=date(2026, 6, 10),
                description="Granddaughter Lily turning 11",
                related_person="Lily",
                source="family_data"
            ),
            LifeEvent(
                event_type=LifeEventType.OTHER,
                event_date=date(2026, 9, 1),
                description="Considering charitable foundation in Margaret's name",
                source="meeting_notes"
            )
        ],
        concerns=[
            Concern(
                topic="legacy planning",
                details="Wants to establish lasting legacy for Margaret. Considering charitable foundation. Also wants grandchildren provided for.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 7, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 11, 20)
            ),
            Concern(
                topic="IHT on estate",
                details="Estate £2.1M. Wants to minimize IHT while supporting grandchildren. NRB + RNRB partially used.",
                severity=ConcernSeverity.MEDIUM,
                date_raised=date(2025, 7, 1),
                status=ConcernStatus.ACTIVE,
                last_discussed=date(2025, 11, 20)
            )
        ],
        policies=[
            Policy(
                policy_type=PolicyType.PENSION,
                provider="NHS Pension Scheme",
                policy_number="NHS-AM-DB",
                current_value=0,
                monthly_contribution=0,
                notes="NHS DB pension from GP career. £38k/year."
            ),
            Policy(
                policy_type=PolicyType.PENSION,
                provider="AJ Bell",
                policy_number="SIPP-AJB-AM",
                current_value=420000,
                monthly_contribution=0,
                notes="Additional voluntary contributions over career. Now in drawdown."
            ),
            Policy(
                policy_type=PolicyType.ISA,
                provider="Charles Stanley",
                policy_number="ISA-CS-AM",
                current_value=285000,
                monthly_contribution=0,
                notes="Equity income focus. Dividends reinvested."
            )
        ],
        total_portfolio_value=2100000,
        risk_profile=RiskProfile(
            attitude_to_risk=RiskAttitude.MEDIUM,
            capacity_for_loss=RiskAttitude.HIGH,
            investment_experience="extensive",
            time_horizon_years=10,
            last_assessed=date(2025, 7, 1),
            notes="Very comfortable with investments. Focus shifting to legacy and charity."
        ),
        meeting_notes=[
            MeetingNote(
                meeting_date=date(2025, 11, 20),
                meeting_type=ContactMethod.IN_PERSON,
                duration_minutes=75,
                summary="Discussed charitable foundation options in Margaret's memory. Also reviewed grandchildren gifting and IHT position.",
                key_points=[
                    "Considering foundation for medical research (Margaret's wish)",
                    "3 grandchildren - wants education funds",
                    "Estate £2.1M - IHT exposure ~£100k currently",
                    "Annual gifting from surplus income"
                ],
                action_items=[
                    "Research charitable foundation options",
                    "Set up grandchildren trusts",
                    "IHT mitigation strategy"
                ],
                concerns_raised=["legacy planning", "IHT on estate"]
            )
        ],
        follow_ups=[
            FollowUp(
                commitment="Present charitable foundation options",
                deadline=date(2026, 1, 31),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 11, 20)
            ),
            FollowUp(
                commitment="Grandchildren education trust setup proposal",
                deadline=date(2026, 2, 15),
                status=FollowUpStatus.PENDING,
                created_date=date(2025, 11, 20)
            )
        ],
        interactions=[
            Interaction(
                interaction_date=datetime(2025, 11, 20, 10, 0),
                method=ContactMethod.IN_PERSON,
                direction="outbound",
                summary="Legacy and charitable planning discussion",
                duration_minutes=75,
                next_action="Foundation research"
            )
        ],
        compliance=ComplianceRecord(
            last_annual_review=date(2025, 11, 20),
            next_review_due=date(2026, 11, 20),
            review_status="completed",
            suitability_confirmed=True,
            suitability_date=date(2025, 11, 20)
        ),
        client_since=date(2010, 6, 1),
        assigned_advisor="Jonathan Hayes",
        tags=["retiree", "widower", "charitable", "legacy-planning", "high-value"],
        notes="Lovely gentleman. Still misses Margaret deeply. Medicine runs in family - both children doctors. Very engaged with grandchildren. Wants to leave meaningful legacy."
    )


def generate_all_clients() -> ClientDatabase:
    """Generate comprehensive client database based on sample documents"""
    
    clients = [
        create_sarah_michael_thompson(),
        create_david_sarah_chen(),
        create_basil_sybil_fawlty(),
        create_james_rebecca_martinez(),
        create_anne_partridge(),
        create_priya_raj_patel(),
        create_rodney_cassandra_trotter(),
        create_hyacinth_richard_bucket(),
        create_keith_candice_lard(),
        create_gareth_cheeseman(),
        create_lisa_rahman(),
        create_emma_john_thompson(),
        create_anthony_makepeace(),
    ]
    
    print(f"Generated {len(clients)} detailed client profiles")
    
    for client in clients:
        concerns_count = len(client.active_concerns)
        follow_ups_count = len(client.pending_follow_ups)
        print(f"  - {client.full_name}: {len(client.policies)} policies, {concerns_count} active concerns, {follow_ups_count} pending follow-ups")
    
    return ClientDatabase(
        clients=clients,
        last_updated=datetime.now(),
        version="2.0.0"
    )


def save_to_json(db: ClientDatabase, filepath: str = "clients.json"):
    """Save client database to JSON"""
    with open(filepath, "w") as f:
        json.dump(db.model_dump(mode="json"), f, indent=2, default=str)
    print(f"\nSaved {len(db.clients)} clients to {filepath}")


if __name__ == "__main__":
    # Generate clients
    client_db = generate_all_clients()
    
    # Save to JSON
    save_to_json(client_db)
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total clients: {len(client_db.clients)}")
    print(f"Clients with overdue reviews: {sum(1 for c in client_db.clients if c.has_overdue_review)}")
    print(f"Clients with active concerns: {sum(1 for c in client_db.clients if c.active_concerns)}")
    print(f"Clients with pending follow-ups: {sum(1 for c in client_db.clients if c.pending_follow_ups)}")

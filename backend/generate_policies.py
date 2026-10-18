import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4B5563"))
        
        # Header
        self.drawString(54, 750, "Apex Financial & Insurance Services — Policy Document")
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(54, 742, letter[0] - 54, 742)
        
        # Footer
        self.line(54, 45, letter[0] - 54, 45)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.drawString(54, 32, "Confidential — Insured Policy Agreement")
        self.restoreState()

def create_health_policy(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=60
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=6
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151")
    )

    story = []
    
    # PAGE 1: Policy Overview, Definitions, Schedule of Benefits
    story.append(Paragraph("APEX COMPREHENSIVE HEALTH INSURANCE POLICY (PLAN GOLD-2026)", title_style))
    story.append(Paragraph("<b>Policy ID:</b> APH-2026-99410 | <b>Underwriter:</b> Apex Assurance Group LLC | <b>Effective Date:</b> January 1, 2026", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("SECTION 1: POLICY OVERVIEW & SCHEDULE OF BENEFITS", h2_style))
    story.append(Paragraph("This Policy Agreement establishes comprehensive health insurance coverage provided by Apex Assurance Group to the Designated Policyholder and enrolled dependents. Coverage is subject to all deductibles, copayments, coinsurance rates, and exclusions outlined herein.", body_style))
    
    schedule_data = [
        ["Benefit Category", "In-Network Benefit", "Out-of-Network Benefit"],
        ["Individual Deductible", "$1,500 per policy year", "$3,000 per policy year"],
        ["Family Deductible", "$3,000 per policy year", "$6,000 per policy year"],
        ["Individual Out-of-Pocket Max", "$5,000 per calendar year", "$10,000 per calendar year"],
        ["Family Out-of-Pocket Max", "$10,000 per calendar year", "$20,000 per calendar year"],
        ["Primary Care Physician (PCP) Visit", "$25 Copayment (deductible waived)", "30% Coinsurance after deductible"],
        ["Specialist Physician Visit", "$50 Copayment (deductible waived)", "40% Coinsurance after deductible"],
        ["Annual Wellness / Preventive Exam", "100% Covered (No Copayment)", "Covered at 70% of allowed charges"],
        ["Urgent Care Center", "$45 Copayment per visit", "30% Coinsurance after deductible"]
    ]
    t = Table(schedule_data, colWidths=[200, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#DBEAFE")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("SECTION 2: DEFINITIONS AND KEY TERMS", h2_style))
    story.append(Paragraph("<b>2.1 Medically Necessary:</b> Healthcare services or supplies that a licensed medical practitioner provides to evaluate, diagnose, or treat an illness, injury, disease, or its symptoms, meeting accepted medical standards.", body_style))
    story.append(Paragraph("<b>2.2 Prior Authorization:</b> Mandatory advance approval required from the insurer prior to receiving elective inpatient admissions, MRI/CT diagnostic imaging, and specialty infusion therapies.", body_style))
    story.append(Paragraph("<b>2.3 Coinsurance:</b> The percentage of covered medical expenses (e.g., 20%) that the Insured must pay after the annual deductible has been met.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 2: Inpatient & Hospital Care, Emergency Services, Surgical Procedures
    story.append(Paragraph("SECTION 3: INPATIENT HOSPITALIZATION & SURGICAL BENEFITS", h2_style))
    story.append(Paragraph("Hospital inpatient room and board is covered for semi-private accommodations up to a maximum duration of 180 consecutive days per benefit period. Private room accommodations are covered only if deemed medically imperative for patient isolation by attending physicians.", body_style))
    story.append(Paragraph("<b>Inpatient Surgery Copay:</b> Inpatient surgeries carry a $250 institutional copayment followed by 20% coinsurance in-network. Out-of-network inpatient hospitalizations are reimbursed at 50% of the Usual, Customary, and Reasonable (UCR) fee benchmark after meeting the out-of-network deductible.", body_style))
    story.append(Paragraph("<b>Intensive Care Unit (ICU):</b> ICU admissions are covered at 90% in-network after deductible, with zero daily dollar cap, provided prior notification is submitted within 24 hours of emergency admission.", body_style))
    
    story.append(Paragraph("SECTION 4: EMERGENCY MEDICAL SERVICES", h2_style))
    story.append(Paragraph("<b>4.1 Emergency Room Visits:</b> A $200 copayment applies per Emergency Room visit. The $200 copayment is completely waived if the Insured is formally admitted to the hospital within 24 hours of arrival.", body_style))
    story.append(Paragraph("<b>4.2 Ground & Air Ambulance:</b> Ground ambulance transportation is covered at 80% coinsurance after deductible up to $2,500 per incident. Air ambulance requires immediate threat to life or limb where ground transit exceeds 45 minutes, reimbursable at 90% up to $25,000 per incident.", body_style))
    story.append(Paragraph("<b>4.3 Non-Emergency ER Penalty:</b> If an Emergency Room visit is diagnosed as non-emergent (e.g. routine prescription refill or minor cold symptoms), an administrative non-emergency surcharge of $150 may be assessed.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 3: Prescription Drugs, Formulary Tiers, Mental Health
    story.append(Paragraph("SECTION 5: PRESCRIPTION DRUG FORMULARY & PHARMACY BENEFITS", h2_style))
    story.append(Paragraph("Prescription benefits are categorized across four formulary tiers. Maintenance medications may be ordered in 90-day supplies through Apex Mail-Order Pharmacy at a discounted copay rate (2.5x the 30-day retail copayment).", body_style))
    
    rx_data = [
        ["Formulary Tier", "30-Day Retail Copay", "90-Day Mail Order Copay", "Notes / Prior Auth"],
        ["Tier 1: Generic", "$10 Copay", "$25 Copay", "No prior authorization required"],
        ["Tier 2: Preferred Brand", "$35 Copay", "$87.50 Copay", "Step therapy may apply"],
        ["Tier 3: Non-Preferred Brand", "$70 Copay", "$175 Copay", "Requires clinical justification"],
        ["Tier 4: Specialty Biologics", "25% Coinsurance (Max $250)", "Not available by mail", "Strict prior authorization required"]
    ]
    t_rx = Table(rx_data, colWidths=[120, 110, 130, 140])
    t_rx.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FEF3C7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#92400E")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FCD34D")),
    ]))
    story.append(t_rx)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("SECTION 6: BEHAVIORAL HEALTH & SUBSTANCE ABUSE TREATMENT", h2_style))
    story.append(Paragraph("<b>6.1 Outpatient Mental Health:</b> Outpatient psychotherapy, psychiatric evaluation, and behavioral counseling sessions carry a $25 copayment per session with no annual limit on outpatient visits, in strict compliance with the Mental Health Parity and Addiction Equity Act.", body_style))
    story.append(Paragraph("<b>6.2 Inpatient Detoxification and Rehabilitation:</b> Inpatient substance abuse detoxification is covered for up to 30 days per calendar year. Residential rehabilitation requires pre-certification from the Apex Behavioral Health Management division.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 4: Pre-Existing Conditions, Waiting Periods, Maternity
    story.append(Paragraph("SECTION 7: PRE-EXISTING CONDITIONS & WAITING PERIODS", h2_style))
    story.append(Paragraph("<b>7.1 Definition:</b> A pre-existing condition is any physical or mental injury, illness, or medical state for which medical advice, diagnosis, care, or treatment was recommended or received during the 6 months prior to the effective date of this policy.", body_style))
    story.append(Paragraph("<b>7.2 Waiting Period Schedule:</b>", body_style))
    story.append(Paragraph("• Standard Pre-Existing Condition Waiting Period: <b>12 consecutive months</b> from the effective date of coverage. Claims arising directly from disclosed pre-existing conditions are excluded during this period.", body_style))
    story.append(Paragraph("• Waiver of Waiting Period: The 12-month waiting period shall be waived in full if the Insured presents proof of continuous prior creditable coverage for at least 12 months with no break in coverage exceeding 63 days.", body_style))
    story.append(Paragraph("• Exceptions: Pre-existing condition waiting periods do NOT apply to pregnancy, childbirth, newborn adoption, or to enrolled individuals under the age of 19.", body_style))
    
    story.append(Paragraph("SECTION 8: MATERNITY, NEWBORN, AND REPRODUCTIVE HEALTH", h2_style))
    story.append(Paragraph("<b>8.1 Maternity Care:</b> Routine prenatal visits are covered at 100% with no copayment. Labor, delivery, and post-partum inpatient hospital care are covered under standard inpatient hospitalization benefits ($250 copay + 20% coinsurance).", body_style))
    story.append(Paragraph("<b>8.2 Newborn Coverage:</b> A newborn child is automatically covered for the first 31 days following birth. The policyholder must submit an enrollment amendment within 31 days to maintain continuous dependent coverage.", body_style))
    story.append(Paragraph("<b>8.3 Infertility Treatment:</b> In vitro fertilization (IVF) and artificial insemination are subject to a lifetime maximum benefit of $15,000 per insured individual.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 5: Exclusions & General Limitations
    story.append(Paragraph("SECTION 9: GENERAL EXCLUSIONS AND NON-COVERED SERVICES", h2_style))
    story.append(Paragraph("The following procedures, treatments, and expenses are strictly excluded from coverage under this policy:", body_style))
    story.append(Paragraph("<b>9.1 Cosmetic Surgery:</b> Elective aesthetic or cosmetic surgeries performed solely for appearance enhancement, including rhinoplasty, liposuction, and breast augmentation without reconstructive oncology necessity.", body_style))
    story.append(Paragraph("<b>9.2 Experimental or Investigational Treatments:</b> Any drugs, devices, medical therapies, or clinical trial procedures not officially approved by the FDA for the diagnosed indication.", body_style))
    story.append(Paragraph("<b>9.3 Alternative Medicine:</b> Acupuncture, homeopathic remedies, naturopathic consultation, and ayurvedic therapies (unless an optional Integrative Medicine Rider has been explicitly purchased).", body_style))
    story.append(Paragraph("<b>9.4 Adult Dental and Routine Vision:</b> Routine adult dental examinations, cleanings, orthodontia, eyeglasses, and laser vision correction (LASIK) are not covered under this health plan. Separate Dental and Vision riders are required.", body_style))
    story.append(Paragraph("<b>9.5 Work-Related Injuries:</b> Injuries sustained in the course of employment that are compensable under Workers' Compensation statutes or employer liability legislation.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 6: Claims Submission, Appeals, Contact Information
    story.append(Paragraph("SECTION 10: CLAIMS PROCEDURES, TIMELINES, AND APPEALS", h2_style))
    story.append(Paragraph("<b>10.1 Timely Filing Deadline:</b> All claims for reimbursement must be submitted within <b>180 calendar days</b> from the date services were rendered. Out-of-network claims submitted after 180 days are subject to administrative denial.", body_style))
    story.append(Paragraph("<b>10.2 Claim Adjudication Timeline:</b> Apex Assurance will adjudicate clean, complete electronic claims within <b>30 business days</b> of receipt. Incomplete claims will receive a Request for Additional Information within 15 days.", body_style))
    story.append(Paragraph("<b>10.3 Grievance and Appeals Process:</b>", body_style))
    story.append(Paragraph("• Level 1 Internal Appeal: The Insured has 180 days from the date of an adverse benefit determination to file a Level 1 appeal. Decisions are rendered within 30 calendar days for standard claims and 72 hours for urgent medical care.", body_style))
    story.append(Paragraph("• Level 2 External Review: If the Level 1 appeal is upheld, the Insured may request an Independent Review Organization (IRO) external review within 4 months of the final internal denial.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Customer Support & Claims Submission:</b><br/>Apex Claims Center, PO Box 9021, Hartford, CT 06101<br/>Phone: 1-800-555-APEX | Portal: https://apex-insurance-claims.internal/submit", callout_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Health Policy generated at: {output_path}")

def create_auto_policy(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=60
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#065F46"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#047857"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=6
    )

    story = []
    
    # PAGE 1: Auto Declarations & Coverages
    story.append(Paragraph("ZENITH PERSONAL AUTO INSURANCE POLICY (PREMIER SHIELD)", title_style))
    story.append(Paragraph("<b>Policy Number:</b> ZNA-2026-77821 | <b>Insurer:</b> Zenith Mutual Casualty Co. | <b>Term:</b> 12 Months", body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("PART A: LIABILITY COVERAGES (BODILY INJURY & PROPERTY DAMAGE)", h2_style))
    story.append(Paragraph("Zenith will pay damages for bodily injury or property damage for which any insured becomes legally responsible because of an auto accident up to the specified limits of liability.", body_style))
    
    cov_data = [
        ["Coverage Component", "Limits of Liability", "Deductible"],
        ["Bodily Injury Liability", "$250,000 per person / $500,000 per accident", "$0"],
        ["Property Damage Liability", "$100,000 per accident", "$0"],
        ["Uninsured / Underinsured Motorist", "$250,000 per person / $500,000 per accident", "$0"],
        ["Collision Coverage", "Actual Cash Value (ACV) less deductible", "$500 Deductible"],
        ["Comprehensive (Other than Collision)", "Actual Cash Value (ACV) less deductible", "$250 Deductible"],
        ["Medical Payments Coverage", "$10,000 per person", "$0"],
        ["Roadside Assistance & Towing", "$150 per occurrence (up to 4 events/year)", "$0"],
        ["Rental Car Reimbursement", "$50 per day (up to 30 days / $1,500 max)", "$0"]
    ]
    t_cov = Table(cov_data, colWidths=[180, 200, 120])
    t_cov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D1FAE5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#065F46")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#A7F3D0")),
    ]))
    story.append(t_cov)
    
    story.append(PageBreak())
    
    # PAGE 2: Collision and Comprehensive Details
    story.append(Paragraph("PART B: COLLISION AND COMPREHENSIVE COVERAGE DETAILS", h2_style))
    story.append(Paragraph("<b>Collision Coverage:</b> Protects against damage to your covered vehicle resulting from impact with another vehicle, an object, or vehicle rollover. The standard collision deductible is $500 per claim. The deductible is waived if the accident was caused 100% by an identified insured Zenith policyholder.", body_style))
    story.append(Paragraph("<b>Comprehensive Coverage:</b> Covers accidental physical damage to your covered auto caused by events other than collision, including theft, vandalism, fire, flood, hail, windstorm, earthquake, explosion, or contact with animals (e.g. deer collision). Standard deductible is $250.", body_style))
    story.append(Paragraph("<b>Glass Repair Deductible Waiver:</b> If damaged vehicle glass or windshield can be repaired via resin injection rather than full replacement, Zenith waives the $250 comprehensive deductible completely.", body_style))
    
    story.append(Paragraph("PART C: ROADSIDE ASSISTANCE & TOWING", h2_style))
    story.append(Paragraph("Roadside assistance is available 24/7/365 across the United States and Canada. Covered roadside services include: towing up to 25 miles from disablement location, flat tire change with customer-supplied spare, battery jump-start, lockout service up to $100, and emergency delivery of up to 2 gallons of fuel.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 3: Exclusions and Unauthorized Drivers
    story.append(Paragraph("PART D: EXCLUSIONS & RESTRICTIONS", h2_style))
    story.append(Paragraph("Coverage under this auto policy does not apply to:", body_style))
    story.append(Paragraph("• <b>Commercial / Rideshare Use:</b> Any vehicle actively being used to carry persons or property for compensation, including driving for Uber, Lyft, DoorDash, or Instacart, unless an explicit Rideshare Endorsement is active.", body_style))
    story.append(Paragraph("• <b>Intentional Acts:</b> Bodily injury or property damage caused intentionally by or at the direction of the insured.", body_style))
    story.append(Paragraph("• <b>Racing and Speed Contests:</b> Any vehicle participating in prearranged speed contests, drag races, or track racing.", body_style))
    story.append(Paragraph("• <b>Custom Equipment / Modification Limit:</b> Aftermarket audio systems, custom rims, or vehicle modifications exceeding $1,500 in value unless specifically declared on Schedule Rider E.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 4: Auto Claims, Diminished Value, Total Loss
    story.append(Paragraph("PART E: CLAIM REPORTING AND SETTLEMENT GUIDELINES", h2_style))
    story.append(Paragraph("<b>Reporting Deadline:</b> The policyholder must report any accident or loss within <b>72 hours</b> of the incident. A police report is mandatory for all accidents involving injury, hit-and-run, or theft claims.", body_style))
    story.append(Paragraph("<b>Total Loss Valuation:</b> A vehicle is determined to be a total loss when estimated repair costs plus salvage value exceed 75% of the vehicle's pre-accident Actual Cash Value (ACV). Settlement is calculated using independent third-party market valuation guides.", body_style))
    story.append(Paragraph("<b>Rental Vehicle Duration:</b> Rental car reimbursement is available for up to a maximum of 30 days during active vehicle repairs. If the vehicle is determined a total loss, rental coverage terminates 72 hours after Zenith makes a formal total loss settlement offer.", body_style))
    
    story.append(PageBreak())
    
    # PAGE 5: OEM Parts, Cancellation & Contact
    story.append(Paragraph("PART F: REPAIR PARTS SPECIFICATION & POLICY CANCELLATION", h2_style))
    story.append(Paragraph("<b>Original Equipment Manufacturer (OEM) Parts:</b> For vehicles within the current model year or previous model year with under 15,000 miles, Zenith authorizes brand-new OEM parts. For older vehicles, certified aftermarket or recycled OEM parts of like kind and quality (LKQ) may be utilized.", body_style))
    story.append(Paragraph("<b>Cancellation Terms:</b> The policyholder may cancel this policy at any time with written notice. Zenith may cancel the policy during the first 60 days for any legal reason with 10 days notice; after 60 days, cancellation by the insurer is restricted to non-payment of premium, material fraud, or driver license suspension.", body_style))
    story.append(Paragraph("<b>Emergency Claims Helpline:</b> 1-888-ZENITH-CAR | Web: https://zenith-auto.internal/claims", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Auto Policy generated at: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    create_health_policy(os.path.join(data_dir, "Apex_Comprehensive_Health_Policy_2026.pdf"))
    create_auto_policy(os.path.join(data_dir, "Zenith_Auto_Comprehensive_Policy.pdf"))

import sys
from lxml import etree
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from reportlab.lib import colors

# XML namespaces
NS = {
    'dcc': "https://ptb.de/dcc",
    'si':  "https://ptb.de/si"
}


def text(el, default=''):
    return el.text.strip() if el is not None and el.text else default

def build_pdf(xml_path, pdf_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    styles = getSampleStyleSheet()
    story = []

    # SOFTWARE USED
    story.append(Paragraph("SOFTWARE USED", styles['Heading2']))
    sw_name = root.find(".//dcc:dccSoftware//dcc:content", namespaces=NS)
    sw_ver  = root.find(".//dcc:dccSoftware//dcc:release",   namespaces=NS)
    story.append(Paragraph(f"Software Name: {text(sw_name)}", styles['Normal']))
    story.append(Paragraph(f"Software Version: {text(sw_ver)}", styles['Normal']))
    story.append(Spacer(1,12))

    # ADMINISTRATIVE DATA – CORE DATA
    story.append(Paragraph("ADMINISTRATIVE DATA", styles['Heading2']))
    core = root.find(".//dcc:coreData", namespaces=NS)
    uid = core.find("dcc:uniqueIdentifier", namespaces=NS)
    bpd = core.find("dcc:beginPerformanceDate", namespaces=NS)
    epd = core.find("dcc:endPerformanceDate",   namespaces=NS)
    loc = core.find("dcc:performanceLocation",  namespaces=NS)
    story.append(Paragraph("CORE DATA", styles['Heading3']))
    story.append(Paragraph(f"Unique Identifier: {text(uid)}", styles['Normal']))
    story.append(Paragraph(f"Start Performance Date: {text(bpd)}", styles['Normal']))
    story.append(Paragraph(f"End Performance Date: {text(epd)}", styles['Normal']))
    story.append(Paragraph(f"Performance Location: {text(loc)}", styles['Normal']))
    story.append(Spacer(1,12))

    # EQUIPMENTS USED
    items = root.findall(".//dcc:item", namespaces=NS)
    # assume first is calibration, second is standard
    cal, std = items
    story.append(Paragraph("EQUIPMENTS USED", styles['Heading2']))

    # STANDARD EQUIPMENT
    story.append(Paragraph("STANDARD EQUIPMENT", styles['Heading3']))
    std_name  = std.find("dcc:name//dcc:content", namespaces=NS)
    std_model = std.find("dcc:model", namespaces=NS)
    std_id    = std.find("dcc:identifications//dcc:identification", namespaces=NS)
    std_sn    = std_id.find("dcc:name//dcc:content", namespaces=NS)
    std_cert  = std.find("dcc:description//dcc:content[1]", namespaces=NS)
    std_trace = std.find("dcc:description//dcc:content[2]", namespaces=NS)
    story.append(Paragraph(f"Standard Equipment Name: {text(std_name)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Model: {text(std_model)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Serial Number: {text(std_sn)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment Cert No.: {text(std_cert)}", styles['Normal']))
    story.append(Paragraph(f"Standard Equipment {text(std_trace)}", styles['Normal'])) # Traceability
    story.append(Spacer(1,12))

    # CALIBRATION EQUIPMENT
    story.append(Paragraph("CALIBRATION EQUIPMENT", styles['Heading3']))
    cal_name   = cal.find("dcc:name//dcc:content", namespaces=NS)
    cal_model  = cal.find("dcc:model", namespaces=NS)
    cal_id     = cal.find("dcc:identifications//dcc:identification", namespaces=NS)
    cal_sn     = cal_id.find("dcc:name//dcc:content", namespaces=NS)
    descs      = cal.findall("dcc:description//dcc:content", namespaces=NS)
    story.append(Paragraph(f"Calibration Equipment Name: {text(cal_name)}", styles['Normal']))
    story.append(Paragraph(f"Calibration Equipment Model: {text(cal_model)}", styles['Normal']))
    story.append(Paragraph(f"Calibration Equipment Serial Number: {text(cal_sn)}", styles['Normal']))
    # description lines
    story.append(Paragraph(f"Calibration Equipment {text(descs[0])}", styles['Normal'])) # Capacity
    story.append(Paragraph(f"Calibration Equipment {text(descs[1])}", styles['Normal'])) # Range
    story.append(Paragraph(f"Calibration Equipment {text(descs[2])}", styles['Normal'])) #Resolution
    story.append(Spacer(1,12))

    # CALIBRATION LABORATORY
    lab = root.find(".//dcc:calibrationLaboratory", namespaces=NS)
    code = lab.find("dcc:calibrationLaboratoryCode", namespaces=NS)
    lab_name = lab.find("dcc:contact//dcc:content", namespaces=NS)
    city = lab.find("dcc:contact//dcc:city", namespaces=NS)
    country = lab.find("dcc:contact//dcc:countryCode", namespaces=NS)
    post = lab.find("dcc:contact//dcc:postCode", namespaces=NS)
    street = lab.find("dcc:contact//dcc:street", namespaces=NS)
    story.append(Paragraph("CALIBRATION LABORATORY", styles['Heading2']))
    story.append(Paragraph(f"Laboratory Code: {text(code)}", styles['Normal']))
    story.append(Paragraph(f"Laboratory Name: {text(lab_name)}", styles['Normal']))
    addr = f"{text(street)}, {text(city)}, {text(country)}, {text(post)}"
    story.append(Paragraph(f"Laboratory Address: {addr}", styles['Normal']))
    story.append(Spacer(1,12))

    # RESPONSIBLE PERSON/S
    story.append(Paragraph("RESPONSIBLE PERSON/S", styles['Heading2']))
    for i, rp in enumerate(root.findall(".//dcc:respPerson", namespaces=NS), 1):
        name = rp.find("dcc:person//dcc:content", namespaces=NS)
        role = rp.find("dcc:role", namespaces=NS)
        story.append(Paragraph(f"PERSON {i} NAME: {text(name)}", styles['Normal']))
        story.append(Paragraph(f"PERSON {i} ROLE: {text(role)}", styles['Normal']))
    story.append(Spacer(1,12))

    # CUSTOMER INFORMATION
    cust = root.find(".//dcc:customer", namespaces=NS)
    cname = cust.find("dcc:name//dcc:content", namespaces=NS)
    cloc  = cust.find("dcc:location//dcc:content", namespaces=NS)
    story.append(Paragraph("CUSTOMER INFORMATION", styles['Heading2']))
    story.append(Paragraph(f"Customer Name: {text(cname)}", styles['Normal']))
    story.append(Paragraph(f"Customer Location: {text(cloc)}", styles['Normal']))
    story.append(Spacer(1,12))

    # MEASUREMENT RESULTS
    story.append(Paragraph("MEASUREMENT RESULTS", styles['Heading2']))
    meas = root.find(".//dcc:measurementResults", namespaces=NS)
    mname = meas.find("dcc:name//dcc:content", namespaces=NS)
    story.append(Paragraph(f"Calibration Equipment Name: {text(mname)}", styles['Normal']))
    # used method
    um = meas.find(".//dcc:usedMethod", namespaces=NS)
    unc_desc = um.find("dcc:description//dcc:content", namespaces=NS)
    story.append(Paragraph("Used Methods", styles['Heading3']))
    story.append(Paragraph(f"Uncertainty: {text(unc_desc)}", styles['Normal']))
    story.append(Spacer(1,12))
    # influence conditions
    story.append(Paragraph("InfluenceConditions", styles['Heading3']))
    for ref in [("basic_temperature","Temperature"),("basic_humidityRelative","Humidity")]:
        ic = meas.find(f".//dcc:influenceCondition[@refType='{ref[0]}']", namespaces=NS)
        val = ic.find("dcc:data//si:value", namespaces=NS)
        unit= ic.find("dcc:data//si:unit", namespaces=NS)
        story.append(Paragraph(f"{ref[1]}: {text(val)} {text(unit)}", styles['Normal']))
    story.append(Spacer(1,12))


   # Results table
    story.append(Paragraph("Results", styles['Heading3']))
    results = meas.findall(".//dcc:result", namespaces=NS)

    # define a header paragraph style to allow word wrapping and centering
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], alignment=1)
    # 1) Column headers from <dcc:name>, wrapped as Paragraphs to avoid overlap
    headers = [
        Paragraph(text(r.find("dcc:name//dcc:content", namespaces=NS), 'null'), header_style)
        for r in results
    ]

    # 2) Extract raw tokens, merge them, and collect units
    data_cols = []
    unit_cols = []
    for r in results:
        v_el = r.find(".//si:valueXMLList", namespaces=NS)
        u_el = r.find(".//si:unitXMLList",   namespaces=NS)

        raw_vals = v_el.text.split() if v_el is not None and v_el.text else []
        vals = raw_vals if raw_vals else ['null']

        units = u_el.text.split() if u_el is not None and u_el.text else ['']
        data_cols.append(vals)
        unit_cols.append(units)

    # 3) Build the unit row (take first unit of each column)
    unit_row = [
        u_list[0] if u_list and u_list[0] else ''
        for u_list in unit_cols
    ]

    # 4) Build value rows
    max_rows = max((len(col) for col in data_cols), default=0)
    table_data = [headers, unit_row]
    for i in range(max_rows):
        row = [
            data_cols[j][i] if i < len(data_cols[j]) else 'null'
            for j in range(len(data_cols))
        ]
        table_data.append(row)

    # 5) Create table (repeat both header rows if it spills pages) 
    # everything is centered
    tbl = Table(
        table_data,
        colWidths=[(LETTER[0] - 144) / len(headers)] * len(headers),
        repeatRows=2,
        hAlign='CENTER',               # center the table on the page
        rowHeights=[None] * len(table_data),
    )
    tbl.setStyle(TableStyle([
       # center all cells
       ('ALIGN',         (0, 0),   (-1, -1),  'CENTER'),

       # header row
       ('BACKGROUND',    (0,0),   (-1,0),   colors.HexColor('#4F81BD')),
       ('TEXTCOLOR',     (0,0),   (-1,0),   colors.white),
       ('FONTNAME',      (0,0),   (-1,0),   'Helvetica-Bold'),
       ('FONTSIZE',      (0,0),   (-1,0),   11),
       ('BOTTOMPADDING', (0,0),   (-1,0),   8),

       # unit row
       ('BACKGROUND',    (0,1),   (-1,1),   colors.HexColor('#DCE6F1')),
       ('FONTNAME',      (0,1),   (-1,1),   'Helvetica-Oblique'),

       # alternating row backgrounds
       ('ROWBACKGROUNDS',(0,2),   (-1,-1),  [colors.white, colors.HexColor('#F2F2F2')]),
       ('GRID',          (0,0),   (-1,-1),  0.5, colors.grey),

       # padding for all cells
       ('LEFTPADDING',   (0,0),   (-1,-1),  6),
       ('RIGHTPADDING',  (0,0),   (-1,-1),  6),
       ('TOPPADDING',    (0,0),   (-1,-1),  4),
       ('BOTTOMPADDING', (0,0),   (-1,-1),  4),
    ]))
    story.append(tbl)
    story.append(Spacer(1,12))

    # COMMENT
    story.append(Paragraph("COMMENT", styles['Heading2']))
    cmts = root.findall(".//dcc:comment//dcc:content", namespaces=NS)
    story.append(Paragraph(f"{text(cmts[0])}", styles['Normal'])) # Calibration Procedure
    story.append(Spacer(1,12))
    story.append(Paragraph(f"{text(cmts[1])}", styles['Normal'])) # Remarks

    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER)
    doc.build(story)

if __name__ == "__main__":
    xml_path = r"C:\Users\ADMIN\Documents\GitHub\Digital-Calibration-Certificate-for-National-Metrology-Laboratory-of-the-Philippines\05-2024-FORC-0173_DCC.xml"


    
    pdf_path = os.path.splitext(xml_path)[0] + ".pdf"
    build_pdf(xml_path, pdf_path)
    print(f"PDF generated at: {pdf_path}")

    
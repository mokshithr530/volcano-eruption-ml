"""Create the submission write-up PDF and review presentation."""
from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_results():
    return json.loads((OUT / "metrics.json").read_text())


def report_pdf(results):
    path = ROOT / "report" / "volcano_eruption_prediction_writeup.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=42, leftMargin=42,
                            topMargin=34, bottomMargin=34)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER,
                              fontSize=17, leading=21, textColor=colors.HexColor("#17324D")))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], alignment=TA_CENTER,
                              fontSize=9, leading=11, textColor=colors.HexColor("#555555")))
    styles.add(ParagraphStyle(name="H", parent=styles["Heading2"], fontSize=11, leading=13,
                              spaceBefore=7, spaceAfter=3, textColor=colors.HexColor("#17324D")))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.5, leading=10.5,
                              spaceAfter=4))
    story = [Paragraph("Predicting Eruptive Events at Volcanoes from Earthquake Data", styles["TitleCenter"]),
             Paragraph("UE24CS352A Machine Learning Mini-Project - Section E", styles["Sub"]),
             Paragraph("Muhammad Uzair (PES2UG24CS287) | Mokshithreddy Nallaballe (PES2UG24CS284)", styles["Sub"]), Spacer(1, 8)]
    story += [Paragraph("Problem and objective", styles["H"]), Paragraph(
        "Volcanic unrest often changes the local earthquake pattern. This project asks whether an earthquake catalog can identify the eruptive state of Kilauea's Pu'u 'O'o system. We frame the task as contemporaneous binary classification: for each catalog earthquake, predict whether it occurred during a documented eruptive interval. This is a retrospective study and should not be read as an operational warning system.", styles["BodySmall"])]
    story += [Paragraph("Dataset and target construction", styles["H"]), Paragraph(
        "The project uses 6,485 ANSS/WOVOdat earthquake records from the Pu'u 'O'o area, spanning January 1983 to December 1986. Each record contains timestamp, latitude, longitude, depth, magnitude, and distance from the vent. We read the detailed Pu'u 'O'o eruption chronology from the accompanying Hawaii Center for Volcanology workbook. A label of 1 means the earthquake timestamp falls inside an eruption interval; otherwise the label is 0. The resulting positive rate is {:.1f}%.".format(results["dataset"]["positive_rate"] * 100), styles["BodySmall"])]
    story += [Paragraph("Features and methodology", styles["H"]), Paragraph(
        "The model uses latitude, longitude, depth, magnitude, distance, and earthquake-history features. For each event, the pipeline counts earlier earthquakes and records the maximum earlier magnitude in the previous 1, 7, and 30 days. The current earthquake is excluded from these rolling features. We use a chronological split: 70% training, 15% development, and 15% held-out testing. This avoids allowing future records to inform past examples. We compare a majority baseline, balanced Logistic Regression with standardization, and a balanced Random Forest with 300 trees and maximum depth 15.", styles["BodySmall"])]
    story += [Paragraph("Results", styles["H"])]
    table_data = [["Model", "Accuracy", "Precision", "Recall", "F1", "Kappa", "ROC-AUC"]]
    for m in results["models"]:
        table_data.append([m["model"].replace("_", " ").title(), *(f"{m[k]:.3f}" for k in ["accuracy", "precision", "recall", "f1", "kappa", "roc_auc"])])
    t = Table(table_data, colWidths=[1.55*inch, .65*inch, .65*inch, .62*inch, .52*inch, .62*inch, .68*inch])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")),
                           ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                           ("FONTSIZE", (0,0), (-1,-1), 7.5), ("GRID", (0,0), (-1,-1), .25, colors.HexColor("#B6C4D1")),
                           ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F7")]),
                           ("ALIGN", (1,1), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    lr = next(m for m in results["models"] if m["model"] == "logistic_regression")
    rf = next(m for m in results["models"] if m["model"] == "random_forest")
    story += [t, Spacer(1, 5), Paragraph(
        "The held-out ROC-AUC is useful because the test period has a different event-rate distribution from training. Logistic Regression reaches ROC-AUC {:.3f}, while Random Forest reaches {:.3f}; both outperform the 0.5 baseline when ranking eruptive cases. We select thresholds on the development period rather than tuning on the test set. The Random Forest threshold is {:.2f}, giving test accuracy {:.3f}, F1 {:.3f}, and Cohen's kappa {:.3f}.".format(lr["roc_auc"], rf["roc_auc"], rf["threshold"], rf["accuracy"], rf["f1"], rf["kappa"]), styles["BodySmall"]), PageBreak(), Paragraph("Interpretation and limitations", styles["H"]), Paragraph(
        "Earthquake catalog features contain information associated with Kilauea's eruptive state, especially in the ranking measured by ROC-AUC. Development-set threshold selection improves the Random Forest's balance between false alarms and missed eruptive events, but the result remains sensitive to the time period and label definition. A stronger follow-up should use event-based validation and add waveform/tremor, GPS deformation, gas, and station-quality features. The present model predicts contemporaneous status rather than the time until a future eruption, so it supports a useful educational demonstration but not public safety decisions.", styles["BodySmall"]),
        Image(str(OUT / "roc_curves.png"), width=3.25*inch, height=2.3*inch), Spacer(1, 3), Paragraph("Figure: ROC curves on the held-out chronological test period.", styles["Sub"])]
    story += [Spacer(1, 4), Paragraph("Sources: supplied CS229 report and public reference repository bmullet/PEEVED; ANSS/WOVOdat earthquake catalog; Hawaii Center for Volcanology Kilauea eruption chronology. Project repository: https://github.com/mokshithr530/volcano-eruption-ml", styles["BodySmall"])]
    doc.build(story)
    return path


def add_text(slide, text, x, y, w, h, size=20, color=(35, 52, 70), bold=False, align=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    if align is not None: p.alignment = align
    for run in p.runs:
        run.font.name = "Aptos"; run.font.size = Pt(size); run.font.bold = bold
        run.font.color.rgb = RGBColor(*color)
    return box


def slides_pptx(results):
    prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    navy = (23, 50, 77); orange = (221, 108, 39); grey = (90, 104, 116)
    def base(title, n):
        s = prs.slides.add_slide(blank)
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor(248, 250, 252)
        add_text(s, title, .55, .3, 12.1, .55, 28, navy, True)
        add_text(s, f"Kilauea earthquake catalog study  -  {n}", .55, 7.15, 12, .2, 9, grey)
        return s
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor(*navy)
    add_text(s, "Predicting Eruptive Events\nfrom Earthquake Data", .7, 1.55, 11.8, 1.6, 38, (255,255,255), True, PP_ALIGN.CENTER)
    add_text(s, "UE24CS352A Machine Learning Mini-Project - Section E", .7, 3.35, 11.8, .45, 19, (226,233,239), False, PP_ALIGN.CENTER)
    add_text(s, "Muhammad Uzair  |  Mokshithreddy Nallaballe", .7, 3.82, 11.8, .35, 15, (226,233,239), False, PP_ALIGN.CENTER)
    add_text(s, "Kilauea Pu'u 'O'o eruption-status classification", .7, 4.05, 11.8, .4, 17, (248,174,95), False, PP_ALIGN.CENTER)
    s = base("Research question", 2)
    add_text(s, "Can earthquake-catalog features identify whether Kilauea was erupting when an earthquake occurred?", .85, 1.45, 11.4, 1.0, 30, navy, True, PP_ALIGN.CENTER)
    add_text(s, "Target: contemporaneous eruption status\nScope: retrospective educational model\nInterpretation: signal detection, not operational warning", 1.55, 3.2, 10.2, 1.5, 22, grey, False, PP_ALIGN.CENTER)
    s = base("Data and labels", 3)
    add_text(s, "6,485", .9, 1.4, 2.5, .55, 34, orange, True, PP_ALIGN.CENTER); add_text(s, "earthquake records", .9, 2.0, 2.5, .35, 16, grey, False, PP_ALIGN.CENTER)
    add_text(s, "1983–1986", 4.0, 1.4, 2.5, .55, 34, orange, True, PP_ALIGN.CENTER); add_text(s, "catalog period", 4.0, 2.0, 2.5, .35, 16, grey, False, PP_ALIGN.CENTER)
    add_text(s, "49", 7.1, 1.4, 2.5, .55, 34, orange, True, PP_ALIGN.CENTER); add_text(s, "eruption intervals", 7.1, 2.0, 2.5, .35, 16, grey, False, PP_ALIGN.CENTER)
    add_text(s, "Label 1: event falls inside a documented eruption interval\nLabel 0: event occurs during repose\nPositive rate in engineered data: {:.1f}%".format(results["dataset"]["positive_rate"]*100), 1.2, 3.35, 11, 1.4, 22, navy, False, PP_ALIGN.CENTER)
    s = base("Features and validation", 4)
    add_text(s, "Event features", .85, 1.25, 3.2, .35, 20, orange, True)
    add_text(s, "Latitude, longitude, depth\nMagnitude and distance from vent", .85, 1.75, 4.3, 1.1, 21, navy)
    add_text(s, "History features", 5.05, 1.25, 3.2, .35, 20, orange, True)
    add_text(s, "Counts and maximum magnitude\nin previous 1, 7, and 30 days", 5.05, 1.75, 4.3, 1.1, 21, navy)
    add_text(s, "Chronological split", 9.25, 1.25, 3.2, .35, 20, orange, True)
    add_text(s, "70% train\n15% development\n15% held-out test", 9.25, 1.75, 3.2, 1.5, 21, navy)
    add_text(s, "The current earthquake is excluded from rolling-history features to prevent direct leakage.", .85, 4.5, 11.4, .8, 22, grey, False, PP_ALIGN.CENTER)
    s = base("Models and held-out results", 5)
    headers = ["Model", "Accuracy", "F1", "Kappa", "ROC-AUC"]
    x0, widths = .8, [3.3, 1.55, 1.25, 1.35, 1.55]
    # header background
    shape=s.shapes.add_shape(1, Inches(x0), Inches(1.15), Inches(sum(widths)), Inches(.5)); shape.fill.solid(); shape.fill.fore_color.rgb=RGBColor(*navy); shape.line.fill.background()
    for i,h in enumerate(headers): add_text(s,h,x0+sum(widths[:i]),1.2,widths[i],.35,16,(255,255,255),True,PP_ALIGN.CENTER)
    for row_i,m in enumerate(results["models"]):
        y=1.7+row_i*.65
        vals=[m["model"].replace('_',' ').title(),f'{m["accuracy"]:.3f}',f'{m["f1"]:.3f}',f'{m["kappa"]:.3f}',f'{m["roc_auc"]:.3f}']
        for i,v in enumerate(vals): add_text(s,v,x0+sum(widths[:i]),y,widths[i],.3,15,navy, i==0,PP_ALIGN.CENTER)
    rf = next(m for m in results["models"] if m["model"] == "random_forest")
    lr = next(m for m in results["models"] if m["model"] == "logistic_regression")
    add_text(s,"Random Forest: ROC-AUC {:.3f}, tuned threshold {:.2f}, kappa {:.3f}\nLogistic Regression: ROC-AUC {:.3f}\nThresholds were selected on development data before the held-out test.".format(rf["roc_auc"], rf["threshold"], rf["kappa"], lr["roc_auc"]), .85, 4.35, 11.5, 1.25, 22, grey, False, PP_ALIGN.CENTER)
    s = base("What the model tells us", 6)
    add_text(s, "Earthquake features carry predictive signal in the catalog.", .9, 1.25, 11.5, .6, 28, navy, True, PP_ALIGN.CENTER)
    add_text(s, "The Logistic Regression model ranks held-out eruptive events well by ROC-AUC.\nDevelopment-set threshold tuning makes the Random Forest more balanced on the held-out period.\nThe experiment remains retrospective and should not be treated as an operational alert system.", 1.15, 2.45, 11, 2.2, 23, grey, False, PP_ALIGN.CENTER)
    s = base("Conclusion and next steps", 7)
    add_text(s, "Conclusion", .9, 1.2, 2.4, .35, 21, orange, True)
    add_text(s, "The catalog contains useful information about contemporaneous eruptive status, but this experiment does not forecast an eruption days in advance.", .9, 1.7, 11, .8, 25, navy, True)
    add_text(s, "Next steps", .9, 3.25, 2.4, .35, 21, orange, True)
    add_text(s, "Calibrate thresholds on a development period\nUse blocked/event-based validation\nAdd waveform, tremor, GPS, and gas-emission features", .9, 3.75, 11, 1.5, 23, grey)
    add_text(s, "Repository: github.com/mokshithr530/volcano-eruption-ml", .9, 6.25, 11, .35, 14, orange, False, PP_ALIGN.CENTER)
    path = ROOT / "slides" / "volcano_eruption_prediction_review.pptx"; prs.save(path); return path


if __name__ == "__main__":
    results = load_results()
    print(report_pdf(results))
    print(slides_pptx(results))

import html
import os
import re
import shutil
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Desktop\Car Sales and Servicing Portal website")
OUT_DOCX = ROOT / "Project Evaluation & Product Review Report 2 - AutoHub Corrected.docx"
OUT_TXT = ROOT / "Project Evaluation & Product Review Report 2 - AutoHub Corrected.txt"
ASSET_DIR = ROOT / "report-assets"


def esc(text):
    return html.escape(str(text), quote=True)


def png_size(path):
    with open(path, "rb") as f:
        sig = f.read(24)
    if sig[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    return struct.unpack(">II", sig[16:24])


def rpr(bold=False, italic=False, size=22, color=None):
    parts = []
    if bold:
        parts.append("<w:b/>")
    if italic:
        parts.append("<w:i/>")
    if color:
        parts.append(f'<w:color w:val="{color}"/>')
    parts.append(f'<w:sz w:val="{size}"/>')
    parts.append(f'<w:szCs w:val="{size}"/>')
    return f"<w:rPr>{''.join(parts)}</w:rPr>"


def paragraph(text="", style=None, bold=False, italic=False, size=22, color=None, align=None):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    runs = []
    for idx, part in enumerate(str(text).split("\n")):
        if idx:
            runs.append("<w:r><w:br/></w:r>")
        runs.append(
            f"<w:r>{rpr(bold=bold, italic=italic, size=size, color=color)}"
            f'<w:t xml:space="preserve">{esc(part)}</w:t></w:r>'
        )
    return f"<w:p>{ppr_xml}{''.join(runs)}</w:p>"


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell(text, shade=None, bold=False):
    shd = f'<w:shd w:fill="{shade}"/>' if shade else ""
    return (
        '<w:tc><w:tcPr><w:tcW w:w="2200" w:type="dxa"/>'
        '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tcMar>'
        f"{shd}</w:tcPr>{paragraph(text, bold=bold, size=18)}</w:tc>"
    )


def table(rows):
    tbl = [
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="999999"/>'
        '<w:left w:val="single" w:sz="4" w:color="999999"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="999999"/>'
        '<w:right w:val="single" w:sz="4" w:color="999999"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="999999"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="999999"/></w:tblBorders></w:tblPr>'
    ]
    for i, row in enumerate(rows):
        shade = "D9EAF7" if i == 0 else None
        tbl.append("<w:tr>")
        for item in row:
            tbl.append(cell(item, shade=shade, bold=(i == 0)))
        tbl.append("</w:tr>")
    tbl.append("</w:tbl>")
    return "".join(tbl)


def image_xml(rel_id, path, caption):
    width_px, height_px = png_size(path)
    max_width_emu = int(5.7 * 914400)
    height_emu = int(max_width_emu * height_px / width_px)
    return (
        "<w:p><w:r><w:drawing>"
        '<wp:inline distT="0" distB="0" distL="0" distR="0" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        f'<wp:extent cx="{max_width_emu}" cy="{height_emu}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="1" name="Picture"/>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="0" name="screenshot"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill>'
        f'<a:blip r:embed="{rel_id}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{max_width_emu}" cy="{height_emu}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
        + paragraph(caption, italic=True, size=18)
    )


sections = []

cover = [
    paragraph("PROJECT EVALUATION & PRODUCT REVIEW REPORT", style="Title", bold=True, size=36, align="center"),
    paragraph("CW1B - Software Engineering Coursework", bold=True, size=24, align="center"),
    paragraph("Car Sales and Servicing Portal: AutoHub Portal", size=24, align="center"),
    paragraph(""),
    table([
        ["Module", "Software Engineering and Project Management"],
        ["Student Name", "[Your Full Name]"],
        ["Student ID", "[Your Student ID]"],
        ["Role", "Solo full-stack developer and project manager"],
        ["Technology Stack", "Flask, SQLAlchemy, SQLite, JWT, HTML, CSS, JavaScript"],
        ["Submission Date", "May 2026"],
        ["Word Count", "Approx. 3,700 words"],
    ]),
    paragraph("Confidential - submitted for academic assessment only.", italic=True, size=18, align="center"),
    page_break(),
]

toc = [
    paragraph("Table of Contents", style="Heading1"),
    paragraph("1. Features Implemented"),
    paragraph("2. Testing"),
    paragraph("3. Product Issues & Bug Tracking"),
    paragraph("4. Best Practice & Quality Assurance"),
    paragraph("5. Architectural and Software Design Patterns"),
    paragraph("6. Version Control"),
    paragraph("7. Post-Mortem"),
    paragraph("Appendices"),
    page_break(),
]

body_text = []


def add_heading(text, level=1):
    style = "Heading1" if level == 1 else "Heading2"
    sections.append(paragraph(text, style=style))
    body_text.append(text)


def add_para(text):
    sections.append(paragraph(text))
    body_text.append(text)


def add_bullet(text):
    sections.append(paragraph(f"- {text}"))
    body_text.append(text)


def add_table(rows):
    sections.append(table(rows))
    for row in rows:
        body_text.extend(row)


def add_image(rel_id, filename, caption):
    sections.append(image_xml(rel_id, ASSET_DIR / filename, caption))
    body_text.append(caption)


add_heading("1. Features Implemented")
add_para("The AutoHub Portal is a full-stack car sales and servicing system developed as a two-week, solo project. The product implements the case-study requirement for a portal that supports customers, administrators and service operations. The application is not only a static website: it has a Flask REST API, SQLAlchemy database models, JSON responses, JWT authentication, protected administration routes and a browser-based frontend built with HTML, CSS and vanilla JavaScript. My main objective was to deliver a working minimum viable product while also responding to seven change requests raised during the sprint.")
add_para("The original functional scope covered customer management, secure administration, vehicle and service catalogue management, category listing, text search, test-drive or service booking, and invoicing. These were implemented through separate route modules such as auth_routes.py, vehicle_routes.py, service_routes.py, booking_routes.py and invoice_routes.py. The frontend provides public navigation, login and registration pages, vehicle browsing, booking, invoice and admin screens. The screenshots below show the visible product interface and the report captions identify the relevant evidence.")
add_image("rIdImage1", "fig1-home-annotated.png", "Figure 1: Public home page. Label A shows the navigation routes for home, vehicles, login and registration; Label B shows the product value statement and Browse Vehicles call to action.")
add_para("Authentication and authorisation are implemented through the /api/auth/register and /api/auth/login endpoints. Passwords are not stored directly; the User model uses Werkzeug password hashing utilities, while JWT tokens protect profile, booking, invoice and administration operations. User roles include customer, admin and mechanic, allowing the product to separate ordinary customer journeys from privileged management functions. This is important for the assessment because it demonstrates that the project considered security and access control as a product feature rather than an afterthought.")
add_image("rIdImage2", "fig2-login-annotated.png", "Figure 2: Login screen. Label A identifies the authentication form; Label B highlights the required username and password credentials that connect to the JWT login endpoint.")
add_para("The product management features are centred on vehicles, services, customers, bookings and invoices. Administrators can create, update and delete vehicle and service records through protected API endpoints. Customers can browse available vehicles, filter by fuel type, search from the frontend and create bookings. Invoices and invoice items are represented in the database so that service work and sales activity can be converted into billing records. The database includes models for User, Customer, Vehicle, Service, ServiceBooking, Inventory, Invoice and InvoiceItem, making the implementation broad enough to reflect an actual garage or dealership workflow.")
add_image("rIdImage3", "fig3-vehicles-annotated.png", "Figure 3: Vehicle listing page. Label A shows search and fuel filter controls; Label B indicates the vehicle grid area populated by the backend API.")
add_para("The change requirements were handled using a formal impact assessment. The first four high-value changes became sprint scope: advanced search, intelligent ranking, user reviews and additional service-booking capability. Three later extension changes were also implemented in the backend: administrative monitoring, discount and voucher management, and CSV/JSON bulk import. The decision documents show that promotional placement was initially deferred because it had high business value but high complexity; later backend extensions show that the same change-management discipline was applied when capacity increased. This satisfies the assignment requirement to highlight change requirements, because the report links the requested changes to actual files, routes and models.")
add_para("A notable product-management decision was to treat the change requests as business outcomes rather than isolated coding tasks. Search and ranking answer the customer problem of finding the right vehicle quickly. Reviews answer the trust problem by allowing customers to judge vehicle and service quality from previous experience. Monitoring answers the administrator problem of knowing whether the service is healthy. Discounts and bulk import support operational efficiency because a dealer can run campaigns and load stock data without typing every record manually. This framing made the sprint backlog easier to defend academically: each change has a business reason, a technical implementation and a test or verification trail.")
add_bullet("Advanced search: search_routes.py provides vehicle search, suggestions, popular searches, analytics and click logging.")
add_bullet("Intelligent ranking: ranking_routes.py calculates and exposes ranking scores using price, popularity, recency and inventory status factors.")
add_bullet("Reviews and ratings: review_routes.py supports authenticated review submission, public display, moderation, approval, rejection, edit, delete and analytics.")
add_bullet("Monitoring, discounts and import: monitoring_routes.py, discount_routes.py and import_routes.py extend the MVP into operational administration.")

add_heading("2. Testing")
add_para("The testing strategy followed a practical testing-pyramid approach. Unit tests and model tests were intended to give fast feedback on validation, password handling, model relationships and utility functions. API-level integration tests were used for routes that combine authentication, database access and JSON responses. Manual browser testing supported the frontend because the frontend is a static JavaScript client rather than a component framework with a dedicated UI test runner. The project documentation also includes an API_TESTING.md guide for manual cURL or Postman checks, including authentication, vehicle creation, booking and invoice examples.")
add_para("The most useful testing principle in this project was risk-based selection. Authentication, role checks, review moderation and booking validation were treated as high-risk because failure could expose private data, allow unauthorised administration or create invalid operational records. Cosmetic frontend behaviour was tested more manually because it has lower data-integrity impact. This is not a reason to ignore frontend testing, but it explains why limited sprint time was focused on backend behaviours that protect the product's correctness.")
add_para("Test-driven development was applied most clearly where behaviour could be specified before user interface work: authentication validation, password rules, role-based access, review submission, moderation logic, search permissions and booking validation. The Day 3-5, Day 6-7 and Day 8-9 reports record the intended red-green-refactor rhythm: define the user story, write or identify the expected test case, implement the route or model behaviour, then rerun tests and document the outcome. In practice, the project also used test-after development where the product had to move quickly, especially for frontend pages and later extension endpoints.")
add_table([
    ["Test ID", "Purpose", "Expected Result", "Status"],
    ["TC-001", "Register a valid user through /api/auth/register", "User created; password stored as hash", "Implemented"],
    ["TC-002", "Login with valid credentials", "JWT token returned and user data included", "Implemented"],
    ["TC-003", "Customer attempts admin endpoint", "403 forbidden or admin denial", "Passing in admin tests"],
    ["TC-004", "Admin lists and edits users", "User records returned and role changes accepted", "Passing in user-management tests"],
    ["TC-005", "Submit invalid review rating", "Validation error returned", "Passing in review tests"],
    ["TC-006", "Vehicle search with filters", "Filtered list returned with pagination metadata", "Implemented; fixture errors remain"],
    ["TC-007", "Create service booking with missing fields", "400 validation response", "Passing"],
])
add_para("I reran the test suite during preparation of this report to avoid relying only on earlier summary documents. A broad pytest discovery run first failed because two UTF-16 text result files, test_output.txt and test_results.txt, were collected as tests and could not be decoded as UTF-8. Rerunning against the tests folder collected 124 tests. The current result was 27 passed, 1 failed and 96 setup errors, with measured coverage of 40 percent. The dominant root cause is a fixture/configuration mismatch: tests/conftest.py passes the TestingConfig class into create_app(), while app/__init__.py expects a string key such as 'testing'. This is a test infrastructure defect rather than proof that every route is broken, but it is still a real quality issue.")
add_para("The strongest tested area is the review and moderation system. The Day 10 report records passing cases for review submission, invalid rating handling, duplicate review prevention, public review display, pending review retrieval, approval, rejection, editing and deletion. Admin user-management and authorisation tests also pass in the documented run. However, the automated coverage is not yet at the professional threshold originally targeted in the sprint plan. A realistic final quality gate would therefore include fixing the pytest fixture, excluding generated .txt outputs from collection with pytest.ini, replacing SQLAlchemy Query.get() calls with Session.get(), and rerunning coverage before final release.")

add_heading("3. Product Issues & Bug Tracking")
add_para("Issue and bug management was handled through project documents rather than an external tracker. CHANGE_REQUEST_ANALYSIS.md records the incoming change requests, business value, complexity, stakeholder impact, database impact, API impact and risk level. TWO_WEEK_SPRINT_PLAN.md and DAILY_STANDUP.md then translate the work into sprint activity, while Day 3-5, Day 6-7, Day 8-9 and Day 10 reports act as status evidence. This was appropriate for a solo developer coursework project because it kept the evidence close to the codebase and made the product-management trail auditable.")
add_para("The issue process also separated defects from enhancements. Defects were matters where the current product did not meet an agreed requirement, such as a failed validation path or broken test setup. Enhancements were valuable additions, such as promotional placement or richer monitoring, that could be accepted, negotiated or deferred without making the MVP invalid. This distinction prevented the sprint from becoming unrealistic and helped explain why some work was implemented immediately while other work moved into Phase 2.")
add_table([
    ["Issue", "Priority", "Resolution or Status", "Evidence"],
    ["CR-001 Advanced search", "High", "Implemented in search_routes.py with suggestions and analytics", "Change analysis and Day 6-7 report"],
    ["CR-002 Intelligent ranking", "High", "Implemented in ranking_routes.py with recalculation endpoints", "Day 6-7 report"],
    ["CR-003 Promotional placement", "Medium", "Deferred from MVP due to high complexity and UX risk", "MoSCoW matrix"],
    ["CR-004 Reviews and ratings", "High", "Implemented with moderation and analytics", "Day 8-9 validation"],
    ["CR-005 Monitoring", "Medium", "Implemented as later backend extension", "Complete sprint report"],
    ["CR-006 Discounts/vouchers", "Medium", "Implemented as later backend extension", "Project completion summary"],
    ["CR-007 Bulk import", "Medium", "Implemented with import jobs and duplicate checks", "Import route and tests"],
    ["BUG-TEST-001", "High", "Pytest fixture passes class rather than config key; fix required", "Latest test run"],
])
add_para("Prioritisation used a MoSCoW style decision process. Search, ranking and reviews were treated as Must or high-value Should items because they improve discovery, trust and conversion. Promotional placement was deferred because it introduced marketing complexity and could damage user experience if rushed. Monitoring, discounts and import were later added as admin extensions once the core implementation was in place. This demonstrates sensible scope control: not every request was accepted immediately, and the report can justify why.")
add_para("The main weakness is that the issue process is document-led rather than tool-led. There is no rich issue history with separate issue numbers, comments, assignees and closure dates. For a solo academic project this is acceptable, but a professional team would move the same register into GitHub Issues, GitLab or Jira, attach commits to each ticket and require confirmation testing before closure.")

add_heading("4. Best Practice & Quality Assurance")
add_para("Quality assurance was built around documented process, security controls, modular code organisation and repeatable tests. The project uses a walking-skeleton approach: the Flask application factory, database connection, route registration and frontend pages were established early, then features were added in vertical slices. This reduced integration risk because each feature had to connect through the same layers: browser page, API endpoint, model and database. The ADR document records key decisions such as choosing Flask and SQLAlchemy for rapid delivery, using JWT for stateless authentication and keeping the design three-tier rather than prematurely moving to microservices.")
add_para("Another quality practice was traceability. Requirements were not left as a general wish list; they were broken into user stories, acceptance criteria, complexity estimates and dependencies. The change analysis then extended that traceability by adding stakeholder impact and technical impact. This matters because software quality is partly about proving why the product is shaped the way it is. A marker or maintainer can follow the path from requirement, to sprint plan, to code module, to test evidence and finally to post-mortem reflection.")
add_para("Security practices include password hashing, JWT-protected routes, role-based administration checks, CORS configuration and a .gitignore that excludes .env, database files, logs, coverage files, virtual environments and local artifacts. Sensitive configuration is therefore kept out of version control. Validation is applied in route handlers and utility functions for email, password strength, required fields, review rating boundaries and duplicate prevention. These controls align with common OWASP concerns such as broken access control, weak authentication and accidental exposure of secrets.")
add_para("The project also demonstrates maintainability practices. Route modules are separated by domain, which makes it easier to find and test behaviour. Documentation is unusually complete: development guide, API testing guide, architecture decisions, sprint summaries, change-request analysis and final verification reports all support future maintainers. Self-review checklists appear in the sprint plan and cover tests, hardcoded credentials, response formats, validation and documentation.")
add_para("The QA process is not perfect. There is no automated continuous integration pipeline in the repository, and the current git history has only one commit. The latest test run also shows that the test suite needs configuration repair before it can be used as a reliable release gate. These weaknesses are important because quality assurance is not just having tests; it is having tests that run consistently. My quality recommendation is to add pytest.ini, fix the create_app test fixture, add a GitHub Actions workflow, and require a clean test and coverage result before tagging the coursework submission.")

add_heading("5. Architectural and Software Design Patterns")
add_para("The product follows a three-tier architecture. The presentation tier is the frontend directory, containing static HTML pages, a shared CSS stylesheet and JavaScript modules such as api.js, auth.js, vehicles.js, bookings.js, invoices.js and admin.js. The application tier is the Flask backend, organised through an app factory in app/__init__.py and domain blueprints in app/routes. The data tier is SQLAlchemy using SQLite for development, with configuration support for SQL Server in production. This meets the assignment requirement for evidence of MVC or a variation and database implementation.")
add_para("The backend is best described as an MVC-style REST architecture. SQLAlchemy model classes are the Model layer. Blueprint route functions act as Controllers because they receive HTTP input, validate it, call database operations and return JSON. The View layer is split: JSON responses are the API view for programmatic clients, while the frontend HTML and JavaScript render the user-facing browser view. It is not a pure classical MVC desktop application, but it is an appropriate web variation.")
add_para("The database design is relational and deliberately normalised around business entities. Users can be linked to customers; vehicles can be linked to customers, services, bookings, reviews, ranking metrics and discount records; invoices have invoice items. This avoids storing unrelated information in one large table and makes later reporting possible. For example, review analytics can be calculated per vehicle, discounts can be applied to vehicles or services, and service bookings can be queried by customer, vehicle or status.")
add_para("Several patterns support the design. The application factory pattern allows the Flask app to be created with different configurations for development, testing and production. Blueprints provide modular controllers by domain. Decorators such as jwt_required() and admin_required apply cross-cutting security checks without repeating role logic in every route. SQLAlchemy provides an Active Record style, where model classes represent tables and expose persistence behaviour. The standard JSON response shape also acts as a simple contract between backend and frontend.")
add_table([
    ["Layer", "Implementation Evidence", "Responsibility"],
    ["Presentation", "frontend/pages and frontend/js", "Navigation, forms, vehicle listing and admin screens"],
    ["Application", "backend/app/routes/*.py", "REST controllers, validation, role checks and JSON responses"],
    ["Domain/Data", "backend/app/models.py", "Users, vehicles, services, bookings, invoices, reviews and extensions"],
    ["Configuration", "backend/config.py", "Development, production and testing database settings"],
])
add_para("The design is scalable enough for coursework and a small business MVP. The main architectural risks are the absence of a dedicated service layer for complex business rules, route functions that may grow too large over time, and SQLite's limits under concurrent production use. The ADR already anticipates SQL Server as a production option, which is a sensible migration path.")

add_heading("6. Version Control")
add_para("Git was used for version control and the repository contains 87 tracked files in the current initial commit. The .gitignore file is appropriate for a Python/Flask project because it excludes virtual environments, pycache files, local databases, .env files, logs, coverage outputs and temporary artifacts. The .gitattributes file also helps normalise line endings, which is useful on Windows coursework machines.")
add_para("Version control was also useful as a boundary between product artifacts and local machine artifacts. The virtual environments and SQLite database are present on disk for development, but they are excluded from git so another developer receives source code, tests and documentation rather than machine-specific generated files. This supports repeatability and reduces the risk of accidentally submitting secrets or large binaries.")
add_para("The version-control evidence is mixed. On the positive side, the repository is initialised, the full source tree and documentation set are tracked, and git status shows only two currently modified frontend vehicle files. The initial commit records 23,574 insertions across backend, frontend, tests and documentation, which proves that the project is under source control. The change-request documents also provide a written change-management trail, connecting new requirements to implementation planning.")
add_para("However, effective professional version control should show smaller, meaningful commits over time: for example, one commit for authentication, one for vehicles, one for bookings, one for search, one for reviews and one for monitoring/discount/import extensions. A single large commit reduces traceability and makes rollback difficult. In future work I would use feature branches with names such as feature/authentication, feature/search-ranking and feature/reviews, then merge each branch only after tests and self-review.")
add_table([
    ["Evidence", "Current State", "Evaluation"],
    ["Repository", "main branch with initial commit 688e4ad", "Basic version control present"],
    ["Tracked files", "87 files", "Source, tests and documentation captured"],
    ["Ignored files", ".env, .db, logs, coverage and venv excluded", "Good security and hygiene"],
    ["Commit granularity", "One large commit", "Needs improvement for professional traceability"],
])

add_heading("7. Post-Mortem")
add_para("Overall, the product is close to what the case study required. It delivers a working architecture for a car sales and servicing portal, covers the main user roles, supports inventory and service workflows, implements authentication and administration, and responds to change requirements with search, ranking, reviews, monitoring, discounts and import capability. The product is strongest as a backend/API and project-management submission because the codebase and documents show breadth, planning and reflection.")
add_para("The product was mostly built in the correct way for a two-week solo sprint. Starting with a walking skeleton was the right decision because it made integration visible from the beginning. Using Flask and SQLAlchemy was also suitable: the stack is lightweight, understandable and fast to develop. The modular blueprint structure made the backend easier to extend when change requests arrived. The decision to document architecture and change impact was valuable because it turned the project from a coding exercise into a managed software-engineering project.")
add_para("The main architectural flaw is that business logic is concentrated inside route handlers. This is manageable at coursework scale, but search ranking, discount rules, import processing and review moderation would be easier to test and maintain if moved into service modules. A second weakness is that some route modules use SQLAlchemy Query.get(), which now raises deprecation warnings under SQLAlchemy 2.x. A third issue is that the frontend currently depends on live API responses, so when the backend is unavailable the vehicle grid remains in a loading state. Better error states and seeded demo data would improve the product demo.")
add_para("From a security viewpoint, the project makes several correct choices but still needs production hardening. JWT secrets and database URLs should be provided through environment variables, debug mode must be disabled in production, CORS should be restricted to known frontend origins, and admin endpoints should be reviewed for consistent role enforcement. Rate limiting, refresh-token rotation, password reset emails and audit logging would also improve the security story. The current .gitignore helps prevent secrets and local databases from being committed, which is a strong baseline.")
add_para("Scalability is adequate for a small dealership demo but would need work for real usage. SQLite is convenient for development but should be replaced by SQL Server or PostgreSQL in production. Search and ranking calculations may need indexing or cached scores as inventory grows. Bulk import should run asynchronously for large files, with background jobs and progress reporting. Monitoring endpoints are a useful start, but production observability would also include structured logs, alert thresholds and dashboard visualisation.")
add_para("The biggest lesson from the project is that implementation speed and evidence quality must be balanced. I produced many features and extensive documentation, but the latest test run shows that automated verification can fall behind when configuration changes are not kept aligned with fixtures. That is a genuine professional lesson: a feature is not fully done until its tests are reliable in a clean environment. Another lesson is that change management is easier when requests are assessed before coding. The MoSCoW analysis prevented every stakeholder request from entering the sprint blindly.")
add_para("The project also changed my understanding of full-stack responsibility. As the solo developer I could not treat frontend, backend, database, testing and project management as separate concerns owned by other people. A small change to a model affected routes, tests, frontend assumptions and documentation. This made the role more demanding, but it also made the learning more valuable because I had to think about the product as a whole system rather than a set of disconnected programming exercises.")
add_para("My further development priorities are clear. First, repair pytest configuration and raise coverage above the planned threshold. Second, add a CI workflow so every push runs the same checks. Third, refactor heavy route handlers into service classes and repositories. Fourth, improve frontend error handling, accessibility and responsive layout. Fifth, strengthen git practice with incremental commits and feature branches. Finally, prepare the required CW1B demo video with a narrated walkthrough: introduction as solo developer and project manager, login, vehicle browsing, admin management, bookings, database operations, change-request features, code review of key route/model files, known defects and security considerations.")
add_para("In conclusion, AutoHub Portal demonstrates a credible full-stack development journey. It is not perfect, and the report should not pretend that it is. The product has strong functional breadth, clear evidence of requirements and change control, and a sound architecture for the assignment. Its remaining weaknesses - especially test configuration, commit granularity and production hardening - are exactly the kind of critical reflection expected in a project evaluation and product review.")

add_heading("Appendices")
add_para("Appendix A - Evidence files used: PROJECT_REQUIREMENTS.md, CHANGE_REQUEST_ANALYSIS.md, ARCHITECTURE_DECISION_RECORD.md, TWO_WEEK_SPRINT_PLAN.md, DAILY_STANDUP.md, DAY_10_TEST_EXECUTION_REPORT.md, FINAL_CONFIRMATION_ALL_CHANGES_IMPLEMENTED.md, backend/app/models.py, backend/app/routes/*.py and frontend/pages/*.html.")
add_para("Appendix B - Demo video checklist: open with name, student ID and role; show the running product; demonstrate login, vehicle browsing, search/filter, bookings, admin screens and selected backend code; discuss change requirements; show test output and known defects; close with lessons learned and future work.")


def document_xml():
    body = "".join(cover + toc + sections)
    sect = (
        "<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
        "w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/></w:sectPr>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f"<w:body>{body}{sect}</w:body></w:document>"
    )


def styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:after="240"/><w:jc w:val="center"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="36"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="280" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="30"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="220" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="2E75B6"/><w:sz w:val="24"/></w:rPr>
  </w:style>
</w:styles>'''


def write_docx():
    images = [
        ("rIdImage1", "fig1-home-annotated.png"),
        ("rIdImage2", "fig2-login-annotated.png"),
        ("rIdImage3", "fig3-vehicles-annotated.png"),
    ]
    rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for idx, (rid, filename) in enumerate(images, start=1):
        rels.append(
            f'<Relationship Id="{rid}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="media/image{idx}.png"/>'
        )
    rels.append("</Relationships>")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Project Evaluation and Product Review Report</dc:title>
<dc:subject>Car Sales and Servicing Portal</dc:subject>
<dc:creator>Codex generated draft for student editing</dc:creator>
<cp:lastModifiedBy>Codex</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Microsoft Word</Application></Properties>'''

    with zipfile.ZipFile(OUT_DOCX, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("word/document.xml", document_xml())
        z.writestr("word/styles.xml", styles_xml())
        z.writestr("word/_rels/document.xml.rels", "".join(rels))
        for idx, (_, filename) in enumerate(images, start=1):
            z.write(ASSET_DIR / filename, f"word/media/image{idx}.png")


plain_report = "\n\n".join(body_text)
word_count = len(re.findall(r"\b[\w'-]+\b", plain_report))
write_docx()
OUT_TXT.write_text(plain_report, encoding="utf-8")
print(f"Wrote: {OUT_DOCX}")
print(f"Wrote: {OUT_TXT}")
print(f"Body word count: {word_count}")

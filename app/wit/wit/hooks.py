app_name = "wit"
app_title = "Wit"
app_publisher = "WIT"
app_description = "WIT customisations for ERPNext"
app_email = "dev@wit.invalid"
app_license = "proprietary"
# required_apps = []

# Fixtures — records shipped as JSON under wit/fixtures/, imported on every
# `bench migrate` and written by `bench export-fixtures --app wit`
# (tools/erpnext_export.py). Ordering matters: Workflow State and
# Workflow Action Master must import before Workflow. Ownership is declared
# in src/ownership.csv — UI edits to these doctypes are overwritten.
fixtures = [
	"Workflow State",
	"Workflow Action Master",
	"Workflow",
	"Custom Field",
	"Property Setter",
	"Print Format",
	"Client Script",
	"Server Script",
	"Email Template",
]

# Includes in <head>
# ------------------
# app_include_js = "/assets/wit/js/wit.js"
# app_include_css = "/assets/wit/css/wit.css"

# DocType events
# ---------------
# doc_events = {
# 	"*": {
# 		"on_update": "wit.events.on_update",
# 	}
# }

# Scheduled tasks
# ---------------
# scheduler_events = {
# 	"daily": ["wit.tasks.daily"],
# }

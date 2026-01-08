# Event Template Feature - Implementation Plan

## Overview

Create an **Event Template** doctype that allows users to save reusable event configurations. Users can then create new Buzz Events from these templates via a "Create from Template" button in the Buzz Event list view.

---

## Part 1: Event Template DocType

### 1.1 Create New DocType: `Event Template`

**Location:** `buzz/events/doctype/event_template/`

**Fields to include (mirroring Buzz Event):**

| Fieldname | Fieldtype | Options/Notes |
|-----------|-----------|---------------|
| `template_name` | Data | **Required** - Name of the template (e.g., "Frappe Webinar Template") |
| `category` | Link | Event Category |
| `host` | Link | Event Host |
| `banner_image` | Attach Image | |
| `short_description` | Small Text | |
| `about` | Text Editor | |
| `medium` | Select | "In Person", "Online" |
| `venue` | Link | Event Venue (conditional on medium) |
| `time_zone` | Autocomplete | |
| `ticket_email_template` | Link | Email Template |
| `ticket_print_format` | Link | Print Format |
| `apply_tax` | Check | |
| `tax_label` | Data | |
| `tax_percentage` | Percent | |
| `auto_send_pitch_deck` | Check | |
| `sponsor_deck_email_template` | Link | Email Template |
| `sponsor_deck_reply_to` | Data | |
| `sponsor_deck_cc` | Small Text | |

**Child Tables:**
| Fieldname | Fieldtype | Options |
|-----------|-----------|---------|
| `payment_gateways` | Table | Event Payment Gateway |
| `sponsor_deck_attachments` | Table | Sponsorship Deck Item |

> **Note:** Schedule items and Featured Speakers are NOT included in templates since every event has unique talks, speakers, and schedule.

**Additional Child Tables for Template-Specific Data:**
| Fieldname | Fieldtype | Options |
|-----------|-----------|---------|
| `template_ticket_types` | Table | Event Template Ticket Type (new) |
| `template_add_ons` | Table | Event Template Add-on (new) |
| `template_custom_fields` | Table | Event Template Custom Field (new) |

### 1.2 Create Child DocTypes for Template

Since Ticket Types, Add-ons, and Custom Fields are linked to events (not child tables), we need template-specific child tables:

#### Event Template Ticket Type
| Fieldname | Fieldtype | Options |
|-----------|-----------|---------|
| `title` | Data | Required |
| `price` | Currency | |
| `currency` | Link | Currency |
| `is_published` | Check | |
| `max_tickets_available` | Int | |
| `auto_unpublish_after` | Date | |

#### Event Template Add-on
| Fieldname | Fieldtype | Options |
|-----------|-----------|---------|
| `title` | Data | Required |
| `price` | Currency | |
| `currency` | Link | Currency |
| `description` | Small Text | |
| `user_selects_option` | Check | |
| `options` | Small Text | |
| `enabled` | Check | |

#### Event Template Custom Field
| Fieldname | Fieldtype | Options |
|-----------|-----------|---------|
| `label` | Data | Required |
| `fieldname` | Data | |
| `fieldtype` | Select | Data, Phone, Email, Select, Date, Number |
| `options` | Small Text | |
| `applied_to` | Select | Booking, Ticket |
| `enabled` | Check | |
| `mandatory` | Check | |
| `placeholder` | Data | |
| `default_value` | Data | |
| `order` | Int | |

---

## Part 2: List View Button & Dialog

### 2.1 Create List View Settings

**File:** `buzz/events/doctype/buzz_event/buzz_event_list.js`

```javascript
frappe.listview_settings["Buzz Event"] = {
    onload: function(listview) {
        // Add "Create from Template" button to page actions
        listview.page.add_inner_button(__("Create from Template"), function() {
            buzz.events.show_create_from_template_dialog();
        });
    }
};
```

### 2.2 Template Selection Dialog

**File:** `buzz/public/js/events/create_from_template.js`

The dialog will have two stages:

**Stage 1: Select Template**
- Link field to select Event Template
- On selection, fetch template data and show Stage 2

**Stage 2: Select What to Copy**
- Dynamic checkboxes based on template content
- Grouped sections:
  - **Event Details** (always shown)
    - [ ] Category
    - [ ] Host
    - [ ] Banner Image
    - [ ] Short Description
    - [ ] About
    - [ ] Medium
    - [ ] Venue
    - [ ] Time Zone
  - **Ticketing Settings**
    - [ ] Tax Settings
    - [ ] Ticket Email Template
    - [ ] Ticket Print Format
  - **Sponsorship Settings**
    - [ ] Auto Send Pitch Deck
    - [ ] Sponsor Deck Email Template
    - [ ] Sponsor Deck Attachments
  - **Payment Gateways** (if template has payment gateways)
    - [ ] Copy Payment Gateways
  - **Ticket Types** (if template has ticket types)
    - [ ] Copy Ticket Types
  - **Add-ons** (if template has add-ons)
    - [ ] Copy Add-ons
  - **Custom Fields** (if template has custom fields)
    - [ ] Copy Custom Fields

### 2.3 Dialog Implementation Pattern

Following the ERPNext/Frappe patterns discovered:

```javascript
frappe.provide("buzz.events");

buzz.events.show_create_from_template_dialog = function() {
    let d = new frappe.ui.Dialog({
        title: __("Create Event from Template"),
        fields: [
            {
                fieldtype: "Link",
                fieldname: "template",
                label: __("Select Template"),
                options: "Event Template",
                reqd: 1,
                change: function() {
                    // Fetch template and update checkboxes
                    buzz.events.update_template_options(d);
                }
            },
            {
                fieldtype: "Section Break",
                fieldname: "options_section",
                label: __("Select What to Copy"),
                depends_on: "eval:doc.template"
            },
            {
                fieldtype: "HTML",
                fieldname: "field_options",
                depends_on: "eval:doc.template"
            }
        ],
        primary_action_label: __("Create Event"),
        primary_action: function(values) {
            buzz.events.create_event_from_template(d, values);
        }
    });

    d.show();
};
```

---

## Part 3: Backend API

### 3.1 Python API Method

**File:** `buzz/events/doctype/buzz_event/buzz_event.py`

```python
@frappe.whitelist()
def create_from_template(template_name, options):
    """
    Create a new Buzz Event from a template.

    Args:
        template_name: Name of the Event Template
        options: Dict of what to copy (e.g., {"category": 1, "ticket_types": 1, ...})

    Returns:
        New Buzz Event document name
    """
    template = frappe.get_doc("Event Template", template_name)
    options = frappe.parse_json(options)

    # Create new event
    event = frappe.new_doc("Buzz Event")
    event.title = f"New Event from {template.template_name}"

    # Copy selected fields
    field_map = {
        "category": "category",
        "host": "host",
        "banner_image": "banner_image",
        "short_description": "short_description",
        "about": "about",
        "medium": "medium",
        "venue": "venue",
        "time_zone": "time_zone",
        "ticket_email_template": "ticket_email_template",
        "ticket_print_format": "ticket_print_format",
        "apply_tax": "apply_tax",
        "tax_label": "tax_label",
        "tax_percentage": "tax_percentage",
        "auto_send_pitch_deck": "auto_send_pitch_deck",
        "sponsor_deck_email_template": "sponsor_deck_email_template",
        "sponsor_deck_reply_to": "sponsor_deck_reply_to",
        "sponsor_deck_cc": "sponsor_deck_cc",
    }

    for option_key, field_name in field_map.items():
        if options.get(option_key):
            event.set(field_name, template.get(field_name))

    # Copy child tables
    if options.get("payment_gateways"):
        for pg in template.payment_gateways:
            event.append("payment_gateways", {"payment_gateway": pg.payment_gateway})


    if options.get("sponsor_deck_attachments"):
        for attachment in template.sponsor_deck_attachments:
            event.append("sponsor_deck_attachments", {"file": attachment.file})

    event.insert()

    # Create linked documents (Ticket Types, Add-ons, Custom Fields)
    if options.get("ticket_types"):
        for tt in template.template_ticket_types:
            ticket_type = frappe.new_doc("Event Ticket Type")
            ticket_type.event = event.name
            ticket_type.title = tt.title
            ticket_type.price = tt.price
            ticket_type.currency = tt.currency
            ticket_type.is_published = tt.is_published
            ticket_type.max_tickets_available = tt.max_tickets_available
            ticket_type.auto_unpublish_after = tt.auto_unpublish_after
            ticket_type.insert()

    if options.get("add_ons"):
        for addon in template.template_add_ons:
            add_on = frappe.new_doc("Ticket Add-on")
            add_on.event = event.name
            add_on.title = addon.title
            add_on.price = addon.price
            add_on.currency = addon.currency
            add_on.description = addon.description
            add_on.user_selects_option = addon.user_selects_option
            add_on.options = addon.options
            add_on.enabled = addon.enabled
            add_on.insert()

    if options.get("custom_fields"):
        for cf in template.template_custom_fields:
            custom_field = frappe.new_doc("Buzz Custom Field")
            custom_field.event = event.name
            custom_field.label = cf.label
            custom_field.fieldname = cf.fieldname
            custom_field.fieldtype = cf.fieldtype
            custom_field.options = cf.options
            custom_field.applied_to = cf.applied_to
            custom_field.enabled = cf.enabled
            custom_field.mandatory = cf.mandatory
            custom_field.placeholder = cf.placeholder
            custom_field.default_value = cf.default_value
            custom_field.order = cf.order
            custom_field.insert()

    return event.name
```

---

## Part 4: "Save as Template" Feature (Reverse Flow)

### 4.1 Custom Button on Buzz Event Form

**File:** `buzz/events/doctype/buzz_event/buzz_event.js`

Add a custom button to save the current event as a template:

```javascript
frappe.ui.form.on("Buzz Event", {
    refresh: function(frm) {
        if (!frm.is_new() && frappe.perm.has_perm("Event Template", 0, "create")) {
            frm.add_custom_button(__("Save as Template"), function() {
                buzz.events.show_save_as_template_dialog(frm);
            }, __("Actions"));
        }
    }
});
```

### 4.2 Save as Template Dialog

Similar to "Create from Template" but in reverse - user selects what to include:

```javascript
buzz.events.show_save_as_template_dialog = function(frm) {
    let d = new frappe.ui.Dialog({
        title: __("Save Event as Template"),
        fields: [
            {
                fieldtype: "Data",
                fieldname: "template_name",
                label: __("Template Name"),
                reqd: 1,
                default: frm.doc.title + " Template"
            },
            {
                fieldtype: "Section Break",
                label: __("Select What to Include")
            },
            // ... checkbox fields similar to create dialog
        ],
        primary_action_label: __("Save Template"),
        primary_action: function(values) {
            frappe.call({
                method: "buzz.events.doctype.event_template.event_template.create_template_from_event",
                args: {
                    event_name: frm.doc.name,
                    template_name: values.template_name,
                    options: values
                },
                callback: function(r) {
                    if (r.message) {
                        d.hide();
                        frappe.show_alert({
                            message: __("Template {0} created successfully", [r.message]),
                            indicator: "green"
                        });
                        frappe.set_route("Form", "Event Template", r.message);
                    }
                }
            });
        }
    });
    d.show();
};
```

### 4.3 Backend API for Save as Template

**File:** `buzz/events/doctype/event_template/event_template.py`

```python
@frappe.whitelist()
def create_template_from_event(event_name, template_name, options):
    """
    Create an Event Template from an existing Buzz Event.

    Args:
        event_name: Name of the source Buzz Event
        template_name: Name for the new template
        options: Dict of what to include

    Returns:
        New Event Template document name
    """
    event = frappe.get_doc("Buzz Event", event_name)
    options = frappe.parse_json(options)

    template = frappe.new_doc("Event Template")
    template.template_name = template_name

    # Copy selected fields from event to template
    # ... similar logic to create_from_template but reversed

    # Copy linked documents (Ticket Types, Add-ons, Custom Fields)
    if options.get("ticket_types"):
        ticket_types = frappe.get_all("Event Ticket Type",
            filters={"event": event_name},
            fields=["*"]
        )
        for tt in ticket_types:
            template.append("template_ticket_types", {
                "title": tt.title,
                "price": tt.price,
                "currency": tt.currency,
                # ... other fields
            })

    # Similar for add-ons and custom fields

    template.insert()
    return template.name
```

---

## Part 5: Permissions

### 5.1 Event Template DocType Permissions

The Event Template doctype will have permissions for the **Event Manager** role:

| Role | Read | Write | Create | Delete | Submit | Cancel |
|------|------|-------|--------|--------|--------|--------|
| Event Manager | ✓ | ✓ | ✓ | ✓ | - | - |
| System Manager | ✓ | ✓ | ✓ | ✓ | - | - |

### 5.2 Permission Checks in Code

```python
# In create_from_template
if not frappe.has_permission("Event Template", "read"):
    frappe.throw(_("You don't have permission to use templates"))

if not frappe.has_permission("Buzz Event", "create"):
    frappe.throw(_("You don't have permission to create events"))

# In create_template_from_event
if not frappe.has_permission("Event Template", "create"):
    frappe.throw(_("You don't have permission to create templates"))
```

---

## Part 6: Implementation Steps

### Step 1: Create DocTypes
1. Create `Event Template` doctype with all fields and Event Manager permissions
2. Create `Event Template Ticket Type` child doctype
3. Create `Event Template Add-on` child doctype
4. Create `Event Template Custom Field` child doctype

### Step 2: Create JavaScript Files
1. Create `buzz_event_list.js` with "Create from Template" button
2. Create `create_from_template.js` with dialog logic
3. Update `buzz_event.js` with "Save as Template" button
4. Add JS files to `hooks.py`

### Step 3: Create Python API
1. Add `create_from_template` whitelisted method in `buzz_event.py`
2. Add `create_template_from_event` whitelisted method in `event_template.py`
3. Add permission checks

### Step 4: Testing
1. Create test templates with various configurations
2. Test "Create from Template" dialog functionality
3. Test "Save as Template" from existing events
4. Test event creation with different option combinations
5. Verify all linked documents are created correctly
6. Test permissions for Event Manager role

---

## Part 5: UI/UX Details

### Dialog Layout (Following Frappe Patterns)

```
┌─────────────────────────────────────────────────────────────┐
│  Create Event from Template                              X  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Select Template                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Link Field - Event Template]                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  Select What to Copy                                        │
│                                                             │
│  [Select All]  [Unselect All]                              │
│                                                             │
│  ▼ Event Details                                           │
│    ☑ Category                    ☑ Host                    │
│    ☑ Banner Image                ☑ Short Description       │
│    ☑ About                       ☑ Medium                  │
│    ☑ Venue                       ☑ Time Zone               │
│                                                             │
│  ▼ Ticketing Settings                                      │
│    ☑ Tax Settings                ☑ Ticket Email Template   │
│    ☑ Ticket Print Format                                   │
│                                                             │
│  ▼ Sponsorship Settings                                    │
│    ☑ Auto Send Pitch Deck        ☑ Sponsor Deck Email      │
│    ☑ Sponsor Deck Attachments                              │
│                                                             │
│  ▼ Related Documents                                       │
│    ☑ Payment Gateways (3)        ☑ Ticket Types (4)        │
│    ☑ Add-ons (2)                 ☑ Custom Fields (6)       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                    [Cancel]  [Create Event] │
└─────────────────────────────────────────────────────────────┘
```

### Checkbox Implementation

Using Frappe's MultiCheck fieldtype pattern:

```javascript
{
    fieldtype: "MultiCheck",
    fieldname: "event_details",
    label: __("Event Details"),
    columns: 2,
    options: [
        { label: __("Category"), value: "category", checked: true },
        { label: __("Host"), value: "host", checked: true },
        { label: __("Banner Image"), value: "banner_image", checked: true },
        // ... more options
    ]
}
```

Or using HTML field with custom rendering (more flexible):

```javascript
{
    fieldtype: "HTML",
    fieldname: "options_html"
}

// Then render custom HTML with checkboxes grouped by section
```

---

## Part 6: File Structure

```
buzz/
├── events/
│   └── doctype/
│       ├── buzz_event/
│       │   ├── buzz_event.py          # Add create_from_template method
│       │   ├── buzz_event.js          # UPDATE: Add "Save as Template" button
│       │   └── buzz_event_list.js     # NEW: List view "Create from Template" button
│       ├── event_template/            # NEW
│       │   ├── event_template.json
│       │   ├── event_template.py      # create_template_from_event method
│       │   └── event_template.js
│       ├── event_template_ticket_type/  # NEW
│       │   └── event_template_ticket_type.json
│       ├── event_template_add_on/       # NEW
│       │   └── event_template_add_on.json
│       └── event_template_custom_field/ # NEW
│           └── event_template_custom_field.json
└── public/
    └── js/
        └── events/
            └── create_from_template.js  # NEW: Dialog logic for both directions
```

---

## Part 7: Unit Tests

### 7.1 Test File Location

**File:** `buzz/events/doctype/event_template/test_event_template.py`

### 7.2 Test Cases

```python
import frappe
from frappe.tests.utils import FrappeTestCase
from buzz.events.doctype.buzz_event.buzz_event import create_from_template
from buzz.events.doctype.event_template.event_template import create_template_from_event


class TestEventTemplate(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test fixtures
        cls.create_test_fixtures()

    @classmethod
    def create_test_fixtures(cls):
        """Create required test data: Event Category, Host, etc."""
        # Create Event Category if not exists
        if not frappe.db.exists("Event Category", "Test Category"):
            frappe.get_doc({
                "doctype": "Event Category",
                "category_name": "Test Category"
            }).insert()

        # Create Event Host if not exists
        if not frappe.db.exists("Event Host", "Test Host"):
            frappe.get_doc({
                "doctype": "Event Host",
                "host_name": "Test Host"
            }).insert()

    def tearDown(self):
        """Clean up test data after each test"""
        frappe.db.rollback()

    # ==================== Template Creation Tests ====================

    def test_create_template_basic(self):
        """Test creating a basic Event Template"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Test Webinar Template",
            "category": "Test Category",
            "host": "Test Host",
            "medium": "Online",
            "about": "Test description"
        })
        template.insert()

        self.assertEqual(template.template_name, "Test Webinar Template")
        self.assertEqual(template.category, "Test Category")
        self.assertEqual(template.medium, "Online")

    def test_create_template_with_ticket_types(self):
        """Test creating a template with ticket types"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Template with Tickets",
            "category": "Test Category",
            "host": "Test Host",
            "template_ticket_types": [
                {
                    "title": "Early Bird",
                    "price": 100,
                    "currency": "INR",
                    "is_published": 1,
                    "max_tickets_available": 50
                },
                {
                    "title": "Regular",
                    "price": 200,
                    "currency": "INR",
                    "is_published": 1
                }
            ]
        })
        template.insert()

        self.assertEqual(len(template.template_ticket_types), 2)
        self.assertEqual(template.template_ticket_types[0].title, "Early Bird")
        self.assertEqual(template.template_ticket_types[0].price, 100)

    def test_create_template_with_add_ons(self):
        """Test creating a template with add-ons"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Template with Add-ons",
            "category": "Test Category",
            "host": "Test Host",
            "template_add_ons": [
                {
                    "title": "T-Shirt",
                    "price": 500,
                    "currency": "INR",
                    "enabled": 1
                },
                {
                    "title": "Lunch",
                    "price": 300,
                    "currency": "INR",
                    "user_selects_option": 1,
                    "options": "Veg\nNon-Veg",
                    "enabled": 1
                }
            ]
        })
        template.insert()

        self.assertEqual(len(template.template_add_ons), 2)
        self.assertEqual(template.template_add_ons[1].user_selects_option, 1)

    def test_create_template_with_custom_fields(self):
        """Test creating a template with custom fields"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Template with Custom Fields",
            "category": "Test Category",
            "host": "Test Host",
            "template_custom_fields": [
                {
                    "label": "Company Name",
                    "fieldname": "company_name",
                    "fieldtype": "Data",
                    "applied_to": "Booking",
                    "mandatory": 1,
                    "enabled": 1
                },
                {
                    "label": "Dietary Preference",
                    "fieldname": "dietary_preference",
                    "fieldtype": "Select",
                    "options": "Veg\nNon-Veg\nVegan",
                    "applied_to": "Ticket",
                    "enabled": 1
                }
            ]
        })
        template.insert()

        self.assertEqual(len(template.template_custom_fields), 2)
        self.assertEqual(template.template_custom_fields[0].mandatory, 1)

    # ==================== Create Event from Template Tests ====================

    def test_create_event_from_template_all_options(self):
        """Test creating an event from template with all options selected"""
        # Create template
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Full Template",
            "category": "Test Category",
            "host": "Test Host",
            "medium": "Online",
            "about": "Template about text",
            "apply_tax": 1,
            "tax_label": "GST",
            "tax_percentage": 18,
            "template_ticket_types": [
                {"title": "Standard", "price": 500, "currency": "INR", "is_published": 1}
            ],
            "template_add_ons": [
                {"title": "Workshop", "price": 1000, "currency": "INR", "enabled": 1}
            ],
            "template_custom_fields": [
                {"label": "Phone", "fieldname": "phone", "fieldtype": "Phone", "applied_to": "Booking", "enabled": 1}
            ]
        })
        template.insert()

        # Create event from template with all options
        options = {
            "category": 1,
            "host": 1,
            "medium": 1,
            "about": 1,
            "apply_tax": 1,
            "tax_label": 1,
            "tax_percentage": 1,
            "ticket_types": 1,
            "add_ons": 1,
            "custom_fields": 1
        }

        event_name = create_from_template(template.name, frappe.as_json(options))
        event = frappe.get_doc("Buzz Event", event_name)

        # Verify event fields
        self.assertEqual(event.category, "Test Category")
        self.assertEqual(event.host, "Test Host")
        self.assertEqual(event.medium, "Online")
        self.assertEqual(event.about, "Template about text")
        self.assertEqual(event.apply_tax, 1)
        self.assertEqual(event.tax_percentage, 18)

        # Verify ticket types created
        ticket_types = frappe.get_all("Event Ticket Type",
            filters={"event": event_name},
            fields=["title", "price"]
        )
        self.assertEqual(len(ticket_types), 1)
        self.assertEqual(ticket_types[0].title, "Standard")

        # Verify add-ons created
        add_ons = frappe.get_all("Ticket Add-on",
            filters={"event": event_name},
            fields=["title", "price"]
        )
        self.assertEqual(len(add_ons), 1)
        self.assertEqual(add_ons[0].title, "Workshop")

        # Verify custom fields created
        custom_fields = frappe.get_all("Buzz Custom Field",
            filters={"event": event_name},
            fields=["label", "fieldtype"]
        )
        self.assertEqual(len(custom_fields), 1)
        self.assertEqual(custom_fields[0].fieldtype, "Phone")

    def test_create_event_from_template_partial_options(self):
        """Test creating an event with only some options selected"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Partial Template",
            "category": "Test Category",
            "host": "Test Host",
            "medium": "In Person",
            "about": "Should not be copied",
            "template_ticket_types": [
                {"title": "VIP", "price": 2000, "currency": "INR", "is_published": 1}
            ]
        })
        template.insert()

        # Only copy category and ticket types
        options = {
            "category": 1,
            "host": 0,
            "medium": 0,
            "about": 0,
            "ticket_types": 1
        }

        event_name = create_from_template(template.name, frappe.as_json(options))
        event = frappe.get_doc("Buzz Event", event_name)

        # Category should be copied
        self.assertEqual(event.category, "Test Category")

        # Host should NOT be copied
        self.assertFalse(event.host)

        # About should NOT be copied
        self.assertFalse(event.about)

        # Ticket types should be copied
        ticket_types = frappe.get_all("Event Ticket Type", filters={"event": event_name})
        self.assertEqual(len(ticket_types), 1)

    def test_create_event_from_template_no_linked_docs(self):
        """Test creating an event without copying linked documents"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "No Linked Docs Template",
            "category": "Test Category",
            "host": "Test Host",
            "template_ticket_types": [
                {"title": "General", "price": 100, "currency": "INR", "is_published": 1}
            ]
        })
        template.insert()

        # Copy fields but not linked docs
        options = {
            "category": 1,
            "host": 1,
            "ticket_types": 0,
            "add_ons": 0,
            "custom_fields": 0
        }

        event_name = create_from_template(template.name, frappe.as_json(options))

        # Event fields should be copied
        event = frappe.get_doc("Buzz Event", event_name)
        self.assertEqual(event.category, "Test Category")

        # No ticket types should be created (except default)
        ticket_types = frappe.get_all("Event Ticket Type",
            filters={"event": event_name, "title": "General"}
        )
        self.assertEqual(len(ticket_types), 0)

    # ==================== Save as Template Tests ====================

    def test_save_event_as_template(self):
        """Test saving an existing event as a template"""
        # Create an event with ticket types and add-ons
        event = frappe.get_doc({
            "doctype": "Buzz Event",
            "title": "Source Event",
            "category": "Test Category",
            "host": "Test Host",
            "start_date": frappe.utils.today(),
            "medium": "Online",
            "about": "Event description"
        })
        event.insert()

        # Create ticket type for the event
        ticket_type = frappe.get_doc({
            "doctype": "Event Ticket Type",
            "event": event.name,
            "title": "Premium",
            "price": 1500,
            "currency": "INR",
            "is_published": 1
        })
        ticket_type.insert()

        # Create add-on for the event
        add_on = frappe.get_doc({
            "doctype": "Ticket Add-on",
            "event": event.name,
            "title": "Swag Kit",
            "price": 500,
            "currency": "INR",
            "enabled": 1
        })
        add_on.insert()

        # Save as template
        options = {
            "category": 1,
            "host": 1,
            "medium": 1,
            "about": 1,
            "ticket_types": 1,
            "add_ons": 1
        }

        template_name = create_template_from_event(
            event.name,
            "My Event Template",
            frappe.as_json(options)
        )
        template = frappe.get_doc("Event Template", template_name)

        # Verify template fields
        self.assertEqual(template.template_name, "My Event Template")
        self.assertEqual(template.category, "Test Category")
        self.assertEqual(template.medium, "Online")

        # Verify ticket types in template
        self.assertEqual(len(template.template_ticket_types), 1)
        self.assertEqual(template.template_ticket_types[0].title, "Premium")
        self.assertEqual(template.template_ticket_types[0].price, 1500)

        # Verify add-ons in template
        self.assertEqual(len(template.template_add_ons), 1)
        self.assertEqual(template.template_add_ons[0].title, "Swag Kit")

    def test_save_event_as_template_partial(self):
        """Test saving event as template with only some options"""
        event = frappe.get_doc({
            "doctype": "Buzz Event",
            "title": "Partial Source Event",
            "category": "Test Category",
            "host": "Test Host",
            "start_date": frappe.utils.today(),
            "medium": "In Person",
            "about": "Should be copied",
            "apply_tax": 1,
            "tax_percentage": 18
        })
        event.insert()

        # Only save category and about
        options = {
            "category": 1,
            "host": 0,
            "medium": 0,
            "about": 1,
            "apply_tax": 0
        }

        template_name = create_template_from_event(
            event.name,
            "Partial Template",
            frappe.as_json(options)
        )
        template = frappe.get_doc("Event Template", template_name)

        self.assertEqual(template.category, "Test Category")
        self.assertEqual(template.about, "Should be copied")
        self.assertFalse(template.host)
        self.assertFalse(template.medium)
        self.assertFalse(template.apply_tax)

    # ==================== Round Trip Tests ====================

    def test_round_trip_event_to_template_to_event(self):
        """Test full round trip: Event -> Template -> New Event"""
        # Step 1: Create original event
        original_event = frappe.get_doc({
            "doctype": "Buzz Event",
            "title": "Original Conference",
            "category": "Test Category",
            "host": "Test Host",
            "start_date": frappe.utils.today(),
            "medium": "In Person",
            "about": "Annual conference description",
            "apply_tax": 1,
            "tax_label": "GST",
            "tax_percentage": 18
        })
        original_event.insert()

        # Add ticket types
        for ticket_data in [
            {"title": "Early Bird", "price": 1000},
            {"title": "Regular", "price": 1500},
            {"title": "VIP", "price": 3000}
        ]:
            frappe.get_doc({
                "doctype": "Event Ticket Type",
                "event": original_event.name,
                "title": ticket_data["title"],
                "price": ticket_data["price"],
                "currency": "INR",
                "is_published": 1
            }).insert()

        # Step 2: Save as template
        template_options = {
            "category": 1,
            "host": 1,
            "medium": 1,
            "about": 1,
            "apply_tax": 1,
            "tax_label": 1,
            "tax_percentage": 1,
            "ticket_types": 1
        }
        template_name = create_template_from_event(
            original_event.name,
            "Conference Template",
            frappe.as_json(template_options)
        )

        # Step 3: Create new event from template
        event_options = {
            "category": 1,
            "host": 1,
            "medium": 1,
            "about": 1,
            "apply_tax": 1,
            "tax_label": 1,
            "tax_percentage": 1,
            "ticket_types": 1
        }
        new_event_name = create_from_template(template_name, frappe.as_json(event_options))
        new_event = frappe.get_doc("Buzz Event", new_event_name)

        # Verify new event matches original
        self.assertEqual(new_event.category, original_event.category)
        self.assertEqual(new_event.host, original_event.host)
        self.assertEqual(new_event.medium, original_event.medium)
        self.assertEqual(new_event.about, original_event.about)
        self.assertEqual(new_event.tax_percentage, original_event.tax_percentage)

        # Verify ticket types match
        new_ticket_types = frappe.get_all("Event Ticket Type",
            filters={"event": new_event_name},
            fields=["title", "price"],
            order_by="price"
        )
        self.assertEqual(len(new_ticket_types), 3)
        self.assertEqual(new_ticket_types[0].title, "Early Bird")
        self.assertEqual(new_ticket_types[0].price, 1000)

    # ==================== Edge Case Tests ====================

    def test_create_event_empty_template(self):
        """Test creating event from template with no optional data"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Empty Template"
        })
        template.insert()

        options = {"category": 1, "host": 1}
        event_name = create_from_template(template.name, frappe.as_json(options))

        # Should create event without errors
        self.assertTrue(frappe.db.exists("Buzz Event", event_name))

    def test_template_name_required(self):
        """Test that template_name is required"""
        template = frappe.get_doc({
            "doctype": "Event Template",
            "category": "Test Category"
        })

        with self.assertRaises(frappe.exceptions.MandatoryError):
            template.insert()

    def test_duplicate_template_name(self):
        """Test handling of duplicate template names"""
        frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Duplicate Name"
        }).insert()

        duplicate = frappe.get_doc({
            "doctype": "Event Template",
            "template_name": "Duplicate Name"
        })

        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            duplicate.insert()

    # ==================== Permission Tests ====================

    def test_event_manager_can_create_template(self):
        """Test that Event Manager role can create templates"""
        # Create test user with Event Manager role
        if not frappe.db.exists("User", "event_manager@test.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "event_manager@test.com",
                "first_name": "Event",
                "last_name": "Manager",
                "roles": [{"role": "Event Manager"}]
            })
            user.insert()

        frappe.set_user("event_manager@test.com")

        try:
            template = frappe.get_doc({
                "doctype": "Event Template",
                "template_name": "Manager Template"
            })
            template.insert()
            self.assertTrue(frappe.db.exists("Event Template", template.name))
        finally:
            frappe.set_user("Administrator")

    def test_guest_cannot_create_template(self):
        """Test that Guest cannot create templates"""
        frappe.set_user("Guest")

        try:
            template = frappe.get_doc({
                "doctype": "Event Template",
                "template_name": "Guest Template"
            })

            with self.assertRaises(frappe.exceptions.PermissionError):
                template.insert()
        finally:
            frappe.set_user("Administrator")
```

### 7.3 Test Fixtures

Create test fixtures file for reusable test data:

**File:** `buzz/events/doctype/event_template/test_records.json`

```json
[
    {
        "doctype": "Event Template",
        "template_name": "Webinar Template",
        "category": "Webinars",
        "host": "Frappe",
        "medium": "Online",
        "about": "Standard webinar template",
        "apply_tax": 1,
        "tax_label": "GST",
        "tax_percentage": 18,
        "template_ticket_types": [
            {
                "title": "Free",
                "price": 0,
                "currency": "INR",
                "is_published": 1
            }
        ]
    },
    {
        "doctype": "Event Template",
        "template_name": "Conference Template",
        "category": "Conferences",
        "host": "Frappe",
        "medium": "In Person",
        "about": "Annual conference template",
        "template_ticket_types": [
            {
                "title": "Early Bird",
                "price": 1000,
                "currency": "INR",
                "is_published": 1
            },
            {
                "title": "Regular",
                "price": 1500,
                "currency": "INR",
                "is_published": 1
            }
        ],
        "template_add_ons": [
            {
                "title": "Workshop Access",
                "price": 500,
                "currency": "INR",
                "enabled": 1
            }
        ]
    }
]
```

### 7.4 Running Tests

```bash
# Run all event template tests
bench --site your-site run-tests --module buzz.events.doctype.event_template

# Run specific test
bench --site your-site run-tests --module buzz.events.doctype.event_template.test_event_template --test test_create_event_from_template_all_options

# Run with verbose output
bench --site your-site run-tests --module buzz.events.doctype.event_template -v
```

---

## Questions for Clarification

1. **Default Ticket Type**: The Buzz Event has a `default_ticket_type` field. Should templates store this preference, and if multiple ticket types are copied, which becomes the default?

---

## Summary

This feature involves:
- **4 new DocTypes** (1 main + 3 child tables)
- **2 new JavaScript files** + 1 update to existing buzz_event.js
- **2 Python API methods** (create_from_template, create_template_from_event)
- **Permissions** for Event Manager role
- **Unit tests** with comprehensive test coverage
- Updates to hooks.py for JS inclusion

### Two User Flows:
1. **Create from Template** (List View → Dialog → New Event)
2. **Save as Template** (Event Form → Dialog → New Template)

### Test Coverage:
- Template creation tests (basic, with ticket types, add-ons, custom fields)
- Create event from template tests (all options, partial options, no linked docs)
- Save as template tests (full, partial)
- Round trip tests (Event → Template → New Event)
- Edge case tests (empty template, required fields, duplicates)
- Permission tests (Event Manager, Guest)

The implementation follows established Frappe/ERPNext patterns for:
- List view buttons (`listview.page.add_inner_button`)
- Dynamic dialogs with conditional fields
- MultiCheck or custom HTML for checkbox groups
- Whitelisted API methods for document creation

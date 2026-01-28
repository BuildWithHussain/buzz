interface DocType {
    name: string;
    creation: string;
    modified: string;
    owner: string;
    modified_by: string;
  }

  interface ChildDocType extends DocType {
    parent?: string;
    parentfield?: string;
    parenttype?: string;
    idx?: number;
  }
  
// Last updated: 2026-01-07 14:41:57.312742
export interface EventCategory extends DocType {
  /** Icon SVG: Code */
  icon_svg?: string;
  /** Enabled: Check */
  enabled: 0 | 1;
  /** Banner Image: Attach Image */
  banner_image?: string;
  /** Slug: Data */
  slug?: string;
  /** Description: Small Text */
  description?: string;
}

// Last updated: 2025-10-28 16:18:05.552522
export interface EventTrack extends DocType {
  /** Event: Link (Buzz Event) */
  event: string;
}

// Last updated: 2025-11-01 11:33:49.166876
export interface EventBookingAttendee extends ChildDocType {
  /** Full Name: Data */
  full_name: string;
  /** Email: Data */
  email: string;
  /** Ticket Type: Link (Event Ticket Type) */
  ticket_type: string;
  /** Currency: Link (Currency) */
  currency: string;
  /** Amount: Currency */
  amount?: any;
  /** Add Ons: Link (Attendee Ticket Add-on) */
  add_ons?: string;
  /** Add On Total: Currency */
  add_on_total?: any;
  /** Number of Add Ons: Int */
  number_of_add_ons?: number;
  /** Custom Fields: JSON */
  custom_fields?: any;
}

// Last updated: 2026-01-05 05:49:52.998996
export interface BuzzCustomField extends DocType {
  /** Event: Link (Buzz Event) */
  event: string;
  /** Applied To: Select */
  applied_to?: 'Booking' | 'Ticket';
  /** Label: Data */
  label: string;
  /** Name: Data */
  fieldname?: string;
  /** Type: Select */
  fieldtype: 'Data' | 'Phone' | 'Email' | 'Select' | 'Date' | 'Number' | 'Multi Select';
  /** Options: Small Text */
  options?: string;
  /** Enabled?: Check */
  enabled: 0 | 1;
  /** Mandatory?: Check */
  mandatory: 0 | 1;
  /** Placeholder: Data */
  placeholder?: string;
  /** Order: Int */
  order?: number;
  /** Default Value: Data */
  default_value?: string;
}

// Last updated: 2025-07-26 12:24:58.729143
export interface EventHost extends DocType {
  /** Logo: Attach Image */
  logo?: string;
  /** By Line: Data */
  by_line?: string;
  /** About: Text Editor */
  about?: string;
  /** Country: Link (Country) */
  country?: string;
  /** Address: Small Text */
  address?: string;
  /** Social Media Links: Table (Social Media Link) */
  social_media_links: SocialMediaLink[];
}

// Last updated: 2025-10-28 16:17:50.389537
export interface SponsorshipTier extends DocType {
  /** Event: Link (Buzz Event) */
  event: string;
  /** Title: Data */
  title: string;
  /** Price: Currency */
  price?: any;
  /** Currency: Link (Currency) */
  currency?: string;
}

// Last updated: 2025-10-28 16:17:49.999214
export interface EventTicketType extends DocType {
  /** Event: Link (Buzz Event) */
  event: string;
  /** Title: Data */
  title: string;
  /** Price: Currency */
  price?: any;
  /** Currency: Link (Currency) */
  currency: string;
  /** Is Published?: Check */
  is_published: 0 | 1;
  /** Max Tickets Available: Int */
  max_tickets_available?: number;
  /** Auto Unpublish After: Date */
  auto_unpublish_after?: string;
  /** Remaining Tickets: Int */
  remaining_tickets?: number;
  /** Tickets Sold: Int */
  tickets_sold?: number;
}

// Last updated: 2025-10-28 17:00:34.475703
export interface SponsorshipEnquiry extends DocType {
  /** Status: Select */
  status?: 'Approval Pending' | 'Payment Pending' | 'Paid' | 'Withdrawn';
  /** Company Name: Data */
  company_name: string;
  /** Company Logo: Attach Image */
  company_logo: string;
  /** Tier: Link (Sponsorship Tier) */
  tier?: string;
  /** Event: Link (Buzz Event) */
  event: string;
  /** Website: Data */
  website?: string;
  /** Country: Link (Country) */
  country?: string;
  /** Phone: Phone */
  phone?: any;
}

// Last updated: 2025-12-06 06:42:53.095763
export interface EventPayment extends DocType {
  /** Payment Received: Check */
  payment_received: 0 | 1;
  /** Reference DocType: Link (DocType) */
  reference_doctype?: string;
  /** Reference Name: Dynamic Link (reference_doctype) */
  reference_docname?: string;
  /** Amount: Currency */
  amount?: any;
  /** Currency: Link (Currency) */
  currency?: string;
  /** User: Link (User) */
  user: string;
  /** Order ID: Data */
  order_id?: string;
  /** Payment ID: Data */
  payment_id?: string;
  /** Payment Gateway: Link (Payment Gateway) */
  payment_gateway?: string;
}

// Last updated: 2025-10-28 16:18:05.658346
export interface EventSponsor extends DocType {
  /** Event: Link (Buzz Event) */
  event: string;
  /** Company Name: Data */
  company_name: string;
  /** Tier: Link (Sponsorship Tier) */
  tier: string;
  /** Company Logo: Attach Image */
  company_logo: string;
  /** Enquiry: Link (Sponsorship Enquiry) */
  enquiry?: string;
  /** Website: Data */
  website?: string;
  /** Country: Link (Country) */
  country?: string;
}

// Last updated: 2025-12-30 13:25:40.498434
export interface EventTicket extends DocType {
  /** Attendee Name: Data */
  attendee_name: string;
  /** Event: Link (Buzz Event) */
  event?: string;
  /** Booking: Link (Event Booking) */
  booking?: string;
  /** Ticket Type: Link (Event Ticket Type) */
  ticket_type: string;
  /** Amended From: Link (Event Ticket) */
  amended_from?: string;
  /** QR Code: Attach Image */
  qr_code?: string;
  /** Add Ons: Table (Ticket Add-on Value) */
  add_ons: TicketAdd-onValue[];
  /** Attendee Email: Data */
  attendee_email: string;
  /** Coupon Used : Link (Bulk Ticket Coupon) */
  coupon_used?: string;
  /** Additional Fields: Table (Additional Field) */
  additional_fields: AdditionalField[];
}

// Last updated: 2025-07-26 12:12:56.836403
export interface ProposalSpeaker extends ChildDocType {
  /** First Name: Data */
  first_name: string;
  /** Last Name: Data */
  last_name?: string;
  /** Email: Data */
  email: string;
}

// Last updated: 2026-01-14 12:38:27.700962
export interface TalkProposal extends DocType {
  /** Title: Data */
  title: string;
  /** Submitted By: Link (User) */
  submitted_by?: string;
  /** Status: Select */
  status?: 'Review Pending' | 'Shortlisted' | 'Accepted' | 'Rejected';
  /** Event: Link (Buzz Event) */
  event: string;
  /** Description: Text Editor */
  description?: string;
  /** Speakers: Table (Proposal Speaker) */
  speakers: ProposalSpeaker[];
  /** Phone: Phone */
  phone?: any;
}

// Last updated: 2025-07-19 12:39:15.298215
export interface TalkSpeaker extends ChildDocType {
  /** Speaker: Link (Speaker Profile) */
  speaker: string;
  /** Social Media Links: Table (Social Media Link) */
  social_media_links: SocialMediaLink[];
}

// Last updated: 2026-01-14 12:38:51.583900
export interface EventTalk extends DocType {
  /** Title: Data */
  title: string;
  /** Speakers: Table (Talk Speaker) */
  speakers: TalkSpeaker[];
  /** Submitted By: Link (User) */
  submitted_by: string;
  /** Proposal: Link (Talk Proposal) */
  proposal?: string;
  /** Event: Link (Buzz Event) */
  event: string;
  /** Description: Text Editor */
  description?: string;
}

// Last updated: 2025-11-01 11:38:22.581796
export interface AdditionalField extends ChildDocType {
  /** Label: Data */
  label?: string;
  /** Fieldname: Data */
  fieldname: string;
  /** Value: Data */
  value: string;
  /** Fieldtype: Data */
  fieldtype?: string;
}

// Last updated: 2025-07-19 12:38:48.912298
export interface SocialMediaLink extends ChildDocType {
  /** URL: Data */
  url: string;
}

// Last updated: 2025-10-27 15:00:22.785410
export interface SpeakerProfile extends DocType {
  /** User: Link (User) */
  user: string;
  /** Display Name: Data */
  display_name?: string;
  /** Designation: Data */
  designation?: string;
  /** Company: Data */
  company?: string;
  /** Display Image: Attach Image */
  display_image?: string;
  /** Social Media Links: Table (Social Media Link) */
  social_media_links: SocialMediaLink[];
}

// Last updated: 2025-10-28 18:54:43.428725
export interface ScheduleItem extends ChildDocType {
  /** Type: Select */
  type: 'Talk' | 'Break';
  /** Talk: Link (Event Talk) */
  talk?: string;
  /** Track: Link (Event Track) */
  track: string;
  /** Start Time: Time */
  start_time: any;
  /** End Time: Time */
  end_time: any;
  /** Description: Data */
  description?: string;
  /** Date: Date */
  date: string;
}

// Last updated: 2025-12-30 11:23:32.333785
export interface UTMParameter extends ChildDocType {
  /** UTM Name: Data */
  utm_name: string;
  /** Value: Small Text */
  value: string;
}

// Last updated: 2026-01-03 17:29:18.102192
export interface EventBooking extends DocType {
  /** Amended From: Link (Event Booking) */
  amended_from?: string;
  /** Attendees: Table (Event Booking Attendee) */
  attendees: EventBookingAttendee[];
  /** Event: Link (Buzz Event) */
  event: string;
  /** User: Link (User) */
  user: string;
  /** Total Amount: Currency */
  total_amount?: any;
  /** Currency: Link (Currency) */
  currency: string;
  /** Net Amount: Currency */
  net_amount?: any;
  /** Tax Percentage: Percent */
  tax_percentage?: number;
  /** Tax Label: Data */
  tax_label?: string;
  /** Tax Amount: Currency */
  tax_amount?: any;
  /** Additional Fields: Table (Additional Field) */
  additional_fields: AdditionalField[];
  /** Naming Series: Select */
  naming_series?: 'B.###';
  /** UTM Parameters: Table (UTM Parameter) */
  utm_parameters: UTMParameter[];
  /** Coupon Code: Link (Buzz Coupon Code) */
  coupon_code?: string;
  /** Discount Amount: Currency */
  discount_amount?: any;
}

// Last updated: 2025-09-25 19:04:45.486029
export interface EventFeaturedSpeaker extends ChildDocType {
  /** Speaker: Link (Speaker Profile) */
  speaker: string;
}

// Last updated: 2025-10-29 17:07:59.277650
export interface SponsorshipDeckItem extends ChildDocType {
  /** File: Attach */
  file: any;
}

// Last updated: 2025-12-22 14:27:25.962536
export interface EventPaymentGateway extends ChildDocType {
  /** Payment Gateway: Link (Payment Gateway) */
  payment_gateway: string;
}

// Last updated: 2026-01-14 11:13:04.386770
export interface BuzzEvent extends DocType {
  /** Title: Data */
  title: string;
  /** Start Date: Date */
  start_date: string;
  /** Category: Link (Event Category) */
  category: string;
  /** Venue: Link (Event Venue) */
  venue?: string;
  /** Medium: Select */
  medium?: 'In Person' | 'Online';
  /** End Date: Date */
  end_date?: string;
  /** Short Description: Small Text */
  short_description?: string;
  /** About: Text Editor */
  about?: string;
  /** Start Time: Time */
  start_time?: any;
  /** End Time: Time */
  end_time?: any;
  /** Host: Link (Event Host) */
  host: string;
  /** Time Zone: Autocomplete */
  time_zone?: string;
  /** Banner Image: Attach Image */
  banner_image?: string;
  /** Is Published?: Check */
  is_published: 0 | 1;
  /** Schedule: Table (Schedule Item) */
  schedule: ScheduleItem[];
  /** Route: Data */
  route?: string;
  /** Meta Image: Attach Image */
  meta_image?: string;
  /** External Registration Page?: Check */
  external_registration_page: 0 | 1;
  /** Registration URL: Data */
  registration_url?: string;
  /** Ticket Print Format: Link (Print Format) */
  ticket_print_format?: string;
  /** Allow Editing Talks After Acceptance: Check */
  allow_editing_talks_after_acceptance: 0 | 1;
  /** Ticket Email Template: Link (Email Template) */
  ticket_email_template?: string;
  /** Featured Speakers: Table (Event Featured Speaker) */
  featured_speakers: EventFeaturedSpeaker[];
  /** Show Sponsorship Section on Website: Check */
  show_sponsorship_section: 0 | 1;
  /** Auto Send Pitch Deck?: Check */
  auto_send_pitch_deck: 0 | 1;
  /** Email Template: Link (Email Template) */
  sponsor_deck_email_template?: string;
  /** CC: Small Text */
  sponsor_deck_cc?: string;
  /** Reply To: Data */
  sponsor_deck_reply_to?: string;
  /** Attachments: Table (Sponsorship Deck Item) */
  sponsor_deck_attachments: SponsorshipDeckItem[];
  /** Default Ticket Type: Link (Event Ticket Type) */
  default_ticket_type?: string;
  /** Free Webinar?: Check */
  free_webinar: 0 | 1;
  /** Proposal: Link (Event Proposal) */
  proposal?: string;
  /** Payment Gateways: Table (Event Payment Gateway) */
  payment_gateways: EventPaymentGateway[];
  /** Apply Tax on Bookings?: Check */
  apply_tax: 0 | 1;
  /** Tax Label: Data */
  tax_label?: string;
  /** Tax Percentage: Percent */
  tax_percentage?: number;
  /** Card Image: Attach Image */
  card_image?: string;
}

// Last updated: 2025-11-08 15:25:00.872093
export interface TicketAdd-on extends DocType {
  /** Price: Currency */
  price?: any;
  /** Currency: Link (Currency) */
  currency?: string;
  /** Event: Link (Buzz Event) */
  event: string;
  /** Title: Data */
  title: string;
  /** Options: Small Text */
  options?: string;
  /** User Selects Option?: Check */
  user_selects_option: 0 | 1;
  /** Description: Small Text */
  description?: string;
  /** Enabled?: Check */
  enabled: 0 | 1;
}

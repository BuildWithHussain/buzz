# Event Schedule Gantt POC

## Overview
This is a Proof of Concept (POC) that demonstrates how Frappe Gantt can be used to improve the event scheduling experience. Instead of manually selecting tracks, start times, and end times in a child table format, this POC provides an intuitive visual scheduling interface.

## Current Problem
The existing scheduling system uses a child table approach where users must:
1. Manually select a track from a dropdown
2. Manually enter start time
3. Manually enter end time
4. Repeat for each talk/break
5. No visual representation of schedule conflicts or timeline

## POC Solution
This POC uses Frappe Gantt to provide:
1. **Visual Timeline**: See all tracks and their schedules at a glance
2. **Drag & Drop**: Move talks between time slots easily
3. **Conflict Detection**: Visual indication of overlapping sessions
4. **Multi-Track Support**: Handle multiple tracks (Day 1 Track 1, Day 2 Track 2, etc.)
5. **Interactive Editing**: Click to edit, drag to reschedule
6. **Export Functionality**: Export schedule data for backend integration

## Features Demonstrated

### 1. Data Structure Mapping
- **Current**: Child table with separate track, start_time, end_time fields
- **POC**: Gantt tasks with start/end datetime, visual track grouping

### 2. Track Management
- Support for multiple tracks (Main Hall, Workshop Room, etc.)
- Color-coded tracks for visual distinction
- Filter by specific track

### 3. Schedule Item Types
- **Talks**: Linked to Event Talk doctype
- **Breaks**: Custom descriptions (Coffee Break, Lunch, etc.)

### 4. Interactive Features
- Add new talks/breaks through modal forms
- Edit existing items by clicking
- Delete items with confirmation
- Drag to reschedule (updates start/end times automatically)
- View mode switching (Day/Week views)

### 5. Data Export
- Export current schedule as JSON
- Ready for backend integration
- Maintains original data structure for compatibility

## Technical Implementation

### Dependencies
- `frappe-gantt`: Core Gantt chart library
- `vue 3`: Frontend framework with Composition API
- `tailwindcss`: Styling

### Key Components
1. **Gantt Configuration**: Custom view modes, popup handling, event callbacks
2. **Data Transformation**: Convert schedule items to Gantt tasks format
3. **CRUD Operations**: Add, edit, delete schedule items
4. **Real-time Updates**: Sync changes between Gantt and data model

### Integration Points
The POC is designed to integrate with existing Frappe doctypes:
- `FE Event`: Parent event document
- `Event Track`: Track definitions
- `Schedule Item`: Individual schedule entries (child table)
- `Event Talk`: Talk details

## Usage

1. **Access**: Navigate to `/schedule-gantt-poc` in the dashboard
2. **View**: See the current schedule across all tracks
3. **Add**: Use "Add New Talk" or "Add Break" buttons
4. **Edit**: Click on any schedule item to edit details
5. **Move**: Drag items to different time slots
6. **Filter**: Select specific tracks from dropdown
7. **Export**: Download schedule data as JSON

## Benefits Over Current System

1. **Visual Context**: See entire schedule at once
2. **Conflict Prevention**: Immediately see overlapping sessions
3. **Efficiency**: Drag-and-drop vs manual time entry
4. **User Experience**: Intuitive vs form-heavy interface
5. **Planning**: Better for schedule coordination and planning

## Next Steps for Integration

1. **Backend API**: Create endpoints to fetch/save schedule data
2. **Real-time Sync**: WebSocket integration for collaborative editing
3. **Validation**: Add business rules (minimum talk duration, break requirements)
4. **Speaker Integration**: Link to speaker availability
5. **Room Capacity**: Factor in venue capacity constraints
6. **Mobile Responsive**: Optimize for mobile schedule management

## File Structure

```
dashboard/src/pages/ScheduleGanttPOC.vue - Main POC component
dashboard/src/router.js - Route configuration
dashboard/src/index.css - Frappe Gantt CSS import
```

## Demo Data

The POC includes sample data representing:
- 4 tracks across 2 days
- Mix of talks and breaks
- Different durations and timing patterns
- Color-coded tracks for visual distinction

This demonstrates how the system would work with real event data while providing a complete scheduling experience.

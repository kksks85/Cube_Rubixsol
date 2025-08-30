📖 **UAV Service Incident - Stage Navigation Feature Guide**

## 🎯 **Overview**
The Stage Navigation feature allows Admin, Manager, and Technician users to navigate to any stage of an incident workflow and edit the necessary fields. This provides complete flexibility in managing the incident lifecycle.

## 🚀 **How to Access**

### Step 1: Open an Incident
- Navigate to UAV Service → Incidents
- Click on any incident to view details

### Step 2: Look for the Floating Button
- On the incident view page, you'll see a floating orange "Edit Stages" button in the bottom-right corner
- The button has a pulse animation to draw attention
- It includes an edit icon and "Edit Stages" text

### Step 3: Click to Navigate
- Click the floating button to open the Stage Navigation interface
- This opens a new page with all available workflow stages

## 🎛️ **User Interface Elements**

### Incident View Page
```
┌─────────────────────────────────────────────────────────┐
│ UAV Service Incident UAV-000001                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ 🎯 Service Workflow Progress                            │
│ ████████████████████████░░░  83%                       │
│ Step 5/6                                                │
│                                                         │
│ [1] [2] [3] [4] [5] [ ]  <- Visual workflow steps      │
│                                                         │
│ ... incident details ...                               │
│                                                         │
│                                    ┌─────────────────┐  │
│                                    │  📝 Edit Stages │  │ <- Floating Button
│                                    └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Stage Navigation Page
```
┌─────────────────────────────────────────────────────────┐
│ 📝 Edit Workflow Stages                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                         │
│ 📋 Incident Summary: UAV-000001                        │
│ Current Status: PREVENTIVE_MAINTENANCE                 │
│                                                         │
│ 🎯 Current Workflow Progress                            │
│ ████████████████████████░░░  83%                       │
│                                                         │
│ 🚀 Navigate to Workflow Stage                          │
│                                                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│ │ 📥 Step 1│ │ 🔬 Step 2│ │ 🔧 Step 3│                │
│ │ Incident │ │ Diagnosis│ │ Repair   │                │
│ │ ✅ DONE  │ │ ✅ DONE  │ │ ✅ DONE  │                │
│ │[Navigate]│ │[Navigate]│ │[Navigate]│                │
│ └──────────┘ └──────────┘ └──────────┘                │
│                                                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│ │ ✅ Step 4│ │ 🔄 Step 5│ │ 🏁 Step 6│                │
│ │ Quality  │ │ Prevent. │ │ Closed   │                │
│ │ ✅ DONE  │ │🔵CURRENT │ │ ⏳PENDING│                │
│ │[Navigate]│ │[ Edit ]  │ │[Navigate]│                │
│ └──────────┘ └──────────┘ └──────────┘                │
└─────────────────────────────────────────────────────────┘
```

## 🎨 **Visual Design Features**

### Floating Button
- **Color**: Orange gradient background
- **Animation**: Gentle pulse effect
- **Position**: Fixed bottom-right corner
- **Responsive**: Adapts to mobile screens
- **Tooltip**: "Navigate to any workflow stage"

### Stage Cards
- **Current Stage**: Blue border and background
- **Completed Stages**: Green border and checkmarks
- **Pending Stages**: Gray border and light background
- **Hover Effects**: Cards lift up with shadow
- **Icons**: Each stage has a descriptive icon

## 🛡️ **Permission System**

### Who Can Access
✅ **Admin Users**: Full access to all features
✅ **Manager Users**: Full access to all features  
✅ **Technician Users**: Full access to all features
❌ **Regular Users**: Cannot access stage navigation

### Safety Features
- Permission checks on every request
- Confirmation prompts for future stage navigation
- Activity logging for audit trails
- Visual feedback for user actions

## 🔄 **Workflow Navigation**

### Available Stages
1. **Incident/Service Request** (📥)
   - Route: View incident details
   - Edit: Basic incident information

2. **Diagnosis & Work Order** (🔬)
   - Route: Diagnosis workflow
   - Edit: Diagnostic findings, work order type

3. **Repair/Maintenance** (🔧)
   - Route: Repair workflow  
   - Edit: Parts, technician hours, costs

4. **Quality Check & Handover** (✅)
   - Route: Quality check workflow
   - Edit: QA verification, airworthiness

5. **Preventive Maintenance** (🔄)
   - Route: Preventive maintenance workflow
   - Edit: Future maintenance schedules

6. **Closed** (🏁)
   - Route: Close incident workflow
   - Edit: Final documentation

## 🎯 **Use Cases**

### Scenario 1: Correction Needed
- Technician notices error in diagnosis
- Uses stage navigation to go back to Step 2
- Corrects diagnostic findings
- System logs the correction

### Scenario 2: Out-of-Order Completion
- Parts arrive early, repair completed
- Jump from Step 2 directly to Step 4 (Quality Check)
- System confirms the skip with user
- Updates workflow appropriately

### Scenario 3: Manager Review
- Manager needs to review all stages
- Uses stage navigation to visit each completed stage
- Verifies all information is correct
- Adds notes where needed

## 📱 **Mobile Responsiveness**

- Floating button adapts to smaller screens
- Stage cards stack vertically on mobile
- Touch-friendly button sizes
- Simplified labels for narrow screens

## 🔍 **Technical Implementation**

### Files Modified
- `app/models.py`: Added `can_edit_stages()` method
- `app/uav_service/routes.py`: Added `edit_stages()` route
- `app/templates/uav_service/view_incident.html`: Added floating button
- `app/templates/uav_service/edit_stages.html`: New stage navigation page

### Key Features
- Role-based access control
- Activity logging system
- URL generation and routing
- Template context management
- JavaScript confirmation prompts
- CSS animations and responsive design

## ✅ **Testing Verification**

The feature has been thoroughly tested:
- ✅ Permission system works correctly
- ✅ URL routing functions properly  
- ✅ Template rendering is successful
- ✅ Database integration verified
- ✅ Activity logging operational
- ✅ Mobile responsiveness confirmed

## 🎉 **Ready for Production**

The Stage Navigation feature is now live and ready for use! 

**To access it:**
1. Go to any UAV Service Incident
2. Look for the orange "Edit Stages" button (bottom-right)
3. Click to open the stage navigation interface
4. Select any stage to navigate to and edit

The system will handle all the routing, permissions, and logging automatically.

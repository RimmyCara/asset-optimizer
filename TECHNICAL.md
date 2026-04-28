# VGM Asset Optimizer - Technical Documentation

## 🔧 Architecture Overview

```
VGM Asset Optimizer
├── backend/
│   ├── app.py          # Flask web server & API
│   └── templates/
│       └── index.html  # Frontend UI
├── database/
│   └── schema.sql      # MySQL database schema
└── docs/
    ├── README.md       # User documentation
    └── TECHNICAL.md    # Technical documentation
```

##  Database Schema

### `assets` Table
```sql
CREATE TABLE assets (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    priority INT NOT NULL,           -- 1=highest, 5=lowest
    status VARCHAR(50) NOT NULL,     -- 'critical', 'high', 'standard', 'low', 'complete'
    date_returned DATE,              -- Optional: when asset was returned
    completed BOOLEAN DEFAULT FALSE  -- Completion status
);
```

### `maintenance_log` Table (Optional)
```sql
CREATE TABLE maintenance_log (
    log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    description TEXT,
    date_logged DATE,
    CONSTRAINT fk_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);
```

##  Backend API Endpoints

### `GET /`
- **Purpose**: Render main application page
- **Response**: HTML template with current assets
- **Logic**: Queries DB for incomplete assets ordered by priority

### `GET /assets`
- **Purpose**: Get all assets (JSON)
- **Response**: `[{"id": 1, "name": "Asset A", "status": "critical", ...}]`

### `POST /add_asset`
- **Request Body**: `{"name": "Asset Name", "status": "critical"}`
- **Response**: `{"message": "Asset added successfully!", "id": asset_id}`
- **Logic**:
  1. Calculate priority from status
  2. Insert into database
  3. Add to in-memory priority queue

### `GET /next_asset`
- **Response**: Asset object or `{"message": "No assets in queue"}`
- **Logic**:
  - If `current_asset` exists: return error message
  - Pop highest priority asset from queue
  - Set as `current_asset`
  - Return asset details

### `PUT /completeAsset/<id>`
- **Purpose**: Mark asset as completed
- **Response**: `{"message": "Asset completed"}`
- **Logic**:
  1. Update database: `completed = TRUE`
  2. Clear `current_asset` if matches
  3. Remove from priority queue

### `GET /completed_assets`
- **Purpose**: Get last 5 completed assets
- **Response**: Array of completed asset objects
- **Query**: `SELECT * FROM assets WHERE completed = TRUE ORDER BY id DESC LIMIT 5`

##  Priority Queue Implementation

### Data Structure
```python
asset_queue = []  # List of tuples: (priority, counter, asset_dict)
current_asset = None  # Currently processing asset
```

### Priority Mapping
```python
priority_map = {
    "critical": 1,      # Highest priority
    "high": 2,
    "standard": 3,
    "low": 4,
    "complete": 5       # Lowest priority
}
```

### Queue Operations
- **Push**: `heapq.heappush(asset_queue, (priority, counter, asset))`
- **Pop**: `_, _, asset = heapq.heappop(asset_queue)`
- **Counter**: `itertools.count()` ensures FIFO within same priority

##  Frontend Architecture

### State Management
```javascript
const state = {
    currentAssetId: '',  // Tracks currently displayed asset
};
```

### Key Functions

#### `loadNextAsset()`
1. Check if asset already displayed
2. Fetch `/next_asset`
3. Update UI with asset details
4. Add "Complete" button
5. Disable "Get Next Asset" button

#### `completeCurrentAsset(id)`
1. Send PUT to `/completeAsset/{id}`
2. Remove asset from UI
3. Clear current asset display
4. Re-enable "Get Next Asset" button
5. Refresh completed assets list

#### `loadCompletedAssets()`
1. Fetch `/completed_assets`
2. Render last 5 completed assets
3. Add staggered fade-in animations

##  CSS Design System

### Variables
```css
:root {
    --primary: #0ea5e9;        /* Blue theme */
    --primary-dark: #0369a1;
    --success: #10b981;        /* Green for completed */
    --warning: #f97316;        /* Orange for high priority */
    --danger: #ef4444;         /* Red for critical */
    --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}
```

### Key Components
- **Cards**: White containers with subtle shadows and hover effects
- **Status Pills**: Colored badges for asset statuses
- **Numbered Counters**: CSS counters for queue positions
- **Animations**: Hover effects, fade-ins, and transforms

## Security Considerations

### Input Validation
- Frontend: Required fields, basic sanitization
- Backend: Parameterized queries prevent SQL injection

### CORS
- Flask default allows local development
- Production: Configure CORS headers

### Session Management
- No user authentication implemented
- Assets are global (no user isolation)

##  Performance Optimizations

### Database Queries
- Indexed on `completed` and `priority` columns
- LIMIT 5 on completed assets query

### Frontend Optimizations
- Minimal DOM manipulation
- Efficient event listeners
- CSS transitions for smooth animations

##  Deployment Considerations

### Production Setup
1. **Environment Variables**: Move DB credentials to env vars
2. **WSGI Server**: Use Gunicorn instead of Flask dev server
3. **Database**: Use connection pooling
4. **Static Files**: Serve CSS/JS from CDN or compressed

### Scaling
- **Queue Persistence**: Save queue to database on shutdown
- **Load Balancing**: Session affinity for queue consistency
- **Database**: Consider read replicas for asset queries

##  Troubleshooting

### Common Issues

**Assets not showing in queue:**
- Check database connection
- Verify `completed = FALSE` in query
- Ensure assets have valid priority values

**Priority not working:**
- Check `calculate_priority()` function
- Verify heap ordering (lower numbers = higher priority)
- Confirm counter increment for FIFO

**Complete button not working:**
- Check network tab for failed requests
- Verify asset ID in URL
- Check database permissions

**UI not updating:**
- Clear browser cache
- Check JavaScript console for errors
- Verify DOM element IDs match

## Future Enhancements

### Short Term
- User authentication and asset ownership
- Bulk asset import/export
- Asset categories and filtering
- Maintenance scheduling

### Long Term
- Real-time notifications
- Mobile app companion
- Analytics dashboard
- Integration with warehouse management systems

---

*For user documentation, see [README.md](../README.md)*</content>
<parameter name="filePath">c:\Users\ibrah\OneDrive\Desktop\VGM Optimizer\TECHNICAL.md
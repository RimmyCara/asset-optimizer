# VGM Asset Optimizer

A web based application for managing and optimizing asset processing in a warehouse environment using a priority-based queue system.

## 📦 Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server
- Flask

### Installation

1. **Clone or download the project**
   ```
   cd "VGM Optimizer"
   ```

2. **Set up the database**
   - Start MySQL server
   - Run the schema file:
   ```sql
   -- Run contents of database/schema.sql in MySQL
   ```

3. **Install dependencies** (if needed)
   ```bash
   pip install flask mysql-connector-python
   ```

4. **Configure database connection** in `backend/app.py`:
   ```python
   db = mysql.connector.connect(
       host="localhost",
       user="your_username",
       password="your_password",
       database="vgm_assets"
   )
   ```

5. **Run the application**
   ```bash
   python backend/app.py
   ```

6. **Open browser** to `http://localhost:5000`

## 🎯 How It Works (Simple Guide)

### Basic Workflow
1. **Add Assets**: Enter asset name and select priority status (Critical → High → Standard → Low)
2. **View Queue**: See all pending assets in priority order with numbered badges
3. **Process Next**: Click "Get Next Asset" to get the highest priority item
4. **Complete**: Click "Complete" on the displayed asset to mark it done
5. **Repeat**: Continue processing assets one by one

### Key Features
- **Priority Queue**: Critical assets are processed first
- **Sequential Processing**: Can only work on one asset at a time
- **Visual Feedback**: Green highlighting shows current asset being processed
- **History**: Last 5 completed assets shown for reference
- **Responsive Design**: Works on desktop and mobile

### Asset Statuses
- **Critical**: Highest priority (red badge)
- **High**: Second priority (orange badge)
- **Standard**: Normal priority (blue badge)
- **Low**: Lowest priority (green badge)

---

*Built with Flask, MySQL, and modern web technologies, by Rimmy Cara.*</content>
<parameter name="filePath">c:\Users\ibrah\OneDrive\Desktop\VGM Optimizer\README.md
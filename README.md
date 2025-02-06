# Clay Mode Addon

**Clay Mode** is a Blender add-on designed to simplify **Material Override** workflows and enhance object grouping using **AI-generated summaries**. It also includes an **automatic updater** for seamless version updates.

## **📌 Features**
- **Material Override Toggle** 🎨
  - Enables and disables Material Override in the **View Layer**.
  - Uses a **custom clay material** that differentiates objects based on their Object Index.

- **AI-Generated Object Grouping** 🧠
  - Uses **Google Gemini AI** to generate **descriptive names** for grouped objects.
  - Creates an **Empty** at the center of selected objects for better organization.

- **Auto-Updater** 🚀
  - Checks for updates automatically or manually.
  - Downloads and installs new versions seamlessly.

---

## **🛠️ Installation**
1. **Download the latest release** from [GitHub Releases](https://github.com/lilbentley/clay_mode/releases).
2. Open **Blender**, go to **Edit > Preferences > Add-ons**.
3. Click **Install**, select the downloaded `.zip` file, and click **Install Add-on**.
4. Enable **Clay Mode** in the add-ons list.

---

## **📖 Usage**

### **🔘 Toggle Material Override**
1. In the **3D Viewport**, locate the **Clay Mode button** in the **header** (next to the Viewport Shading buttons).
2. Click the button to **enable/disable** Material Override.
3. The override applies a **custom Clay Material**:
   - **Objects with Object Index ≤ 0.5 → White (Solid)**
   - **Objects with Object Index > 0.5 → Transparent Glass**
   
### **🧠 AI Grouping**
1. Select multiple objects in the **3D Viewport**.
2. Open the **N-Panel** (`Tool` tab).
3. Click **"Group with AI Summary"**.
4. The AI generates a **descriptive group name** and creates an **Empty** for better organization.

### **🔄 Updating the Addon**
1. Go to **Edit > Preferences > Add-ons > Clay Mode**.
2. Click **Check for Updates**.
3. If an update is available, click **Update** to install the latest version.

---

## **⚙️ Configuration**
### **🔑 Setting Up the API Key**
- Go to **Edit > Preferences > Add-ons > Clay Mode**.
- Enter your **Google Gemini API Key** (required for AI grouping).
- Customize the **AI prompt template** as needed.

---

## **📜 License**
This project is licensed under the **MIT License**.

---

## **📣 Contributors**
- **[@lilbentley](https://github.com/lilbentley)** - Creator
- **[@yourname](https://github.com/yourname)** - Contributor

For contributions, submit a **pull request** or create an **issue** in the repository.

---

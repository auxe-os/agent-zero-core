# **Seedream 4.5 and CmdLab Enhancements**
*Design Document for Hyper-Realistic Image Editing and Snippet Management*

---

## **1. Seedream 4.5 Enhancements**
### **Goal**
Improve **photorealism**, **character consistency**, and **iterative workflows** for Seedream 4.5 while ensuring **performance** and **usability**.

---

### **A. Prompt Generation Logic**
#### **Key Features**
1. **Auto-Enrichment**:
   - Append **photorealism cues** (e.g., "cinematic lighting, 8K, HDR") if missing.
   - Append **technical specs** (e.g., "Sony A7R V, 50mm prime lens, f/2.0") if missing.
   - Append **negative prompts** (e.g., "plastic skin, blurry details") to block artifacts.

2. **Modification Extraction**:
   - Use **regex** to detect user modifications (e.g., "change background to forest").
   - Example regex:
     ```python
     re.compile(r"(change|modify|update|set)\s+(background|outfit|lighting|setting)\s+to\s+([^.]+)")
     ```

3. **Technical Specs Detection**:
   - Use **regex** to detect camera settings (e.g., "Sony A7R V, 50mm prime lens").
   - Example regex:
     ```python
     re.compile(r"(Sony|Canon|Nikon|Fujifilm)\s+[A-Z0-9]+\s*,\s*([0-9]+mm\s+prime\s+lens|[0-9.]+)\s*,\s*f/([0-9.]+)")
     ```

4. **Consistency Block**:
   - Auto-append **Advanced Consistency Preservation** and **Subject Reference** for character consistency.

---

#### **Implementation**
**File**: `python/tools/seedream4_image.py`
**Functions to Add**:
1. `extract_modifications(prompt: str) -> Dict[str, str]`:
   - Extracts modifications (e.g., `{"background": "forest", "outfit": "Barbie brat chav"}`).
2. `has_technical_specs(prompt: str) -> bool`:
   - Checks if the prompt includes technical specs.
3. `append_photorealism_cues(prompt: str) -> str`:
   - Appends photorealism cues if missing.
4. `append_negative_prompts(prompt: str) -> str`:
   - Appends negative prompts to block artifacts.

---

### **B. `image_url` Resolution**
#### **Key Features**
1. **Local Path Handling**:
   - Resolve `img://export_zone/seedream4_12345_0.png` to a public URL using `SEEDREAM4_FILE_BASE_URL`.
   - Fallback to `remote_url` if `SEEDREAM4_FILE_BASE_URL` is not configured.

2. **Error Handling**:
   - Fail with a **clear error message** if neither `SEEDREAM4_FILE_BASE_URL` nor `remote_url` is valid.

---

#### **Implementation**
**File**: `python/tools/seedream4_image.py`
**Functions to Add**:
1. `resolve_image_url(image_url: str) -> str`:
   - Resolves local paths to public URLs.
   - Validates `remote_url` if provided.

---

### **C. Iterative Edits**
#### **Key Features**
1. **Caching**:
   - Cache `seedream4_result` for reuse in subsequent edits.
   - Store `image_url`, `prompt`, and `tool_args` for quick refinements.

2. **Workflow**:
   - Allow users to **select iterative options** (e.g., "adjust lighting", "modify outfit").

---

#### **Implementation**
**File**: `python/tools/seedream4_image.py`
**Functions to Add**:
1. `cache_seedream4_result(result: Dict) -> None`:
   - Caches the result for iterative edits.
2. `get_cached_seedream4_result() -> Dict`:
   - Retrieves the cached result.

---

### **D. Performance**
#### **Key Features**
1. **Default Resolution**:
   - Default to **2K** for faster generation.
   - Allow **4K override** for maximum quality.

2. **User Warnings**:
   - Warn users about slower generation times when selecting 4K.

---

#### **Implementation**
**File**: `python/tools/seedream4_image.py`
**Changes**:
1. Update `DEFAULT_SIZE` to `"2K"`.
2. Add a warning message for 4K resolution.

---

### **E. Response Format**
#### **Key Features**
1. **Structured Output**:
   - Use **tables** for key features (e.g., modifications, resolution, camera settings).
   - Use **expandable sections** for full prompts.
   - Use **iterative options** for quick refinements.

2. **Example Output**:
   ```markdown
   ### 🎨 **Seedream 4.5: Hyper-Realistic Edit Complete**
   **🔍 Prompt Breakdown** *(Click to expand)*
   <details>
   <summary><b>📝 Full Prompt</b></summary>

   ```text
   [Generated Prompt]
   ```
   </details>

   **🎯 Key Features**
   | Attribute          | Specification                          |
   |--------------------|----------------------------------------|
   | **Modifications**  | Scary forest background, Barbie brat chav outfit |
   | **Consistency**    | Advanced Consistency Preservation      |
   | **Resolution**     | 4K (Ultra HD)                          |
   | **Camera**         | Sony A7R V, 50mm prime lens, f/2.0     |

   **📸 Generated Image**
   ![Seedream 4.5 Output](img://export_zone/seedream4_1765006791_0.png)
   *Click to enlarge | [Download](file://export_zone/seedream4_1765006791_0.png)*

   **🔧 Iterative Options** *(Select to refine)*
   - [ ] Adjust lighting (e.g., "golden hour")
   - [ ] Modify outfit (e.g., "add leather jacket")
   - [ ] Change background (e.g., "urban alleyway")
   - [ ] Enhance details (e.g., "hyper-detailed skin texture")
   - [ ] Generate variations (e.g., "3 more poses")
   ```

---

#### **Implementation**
**File**: `python/tools/seedream4_image.py`
**Changes**:
1. Update the `summary` message to use the new format.

---

## **2. CmdLab Feature**
### **Goal**
Enable **snippet and prompt management** for saving, organizing, and reusing prompts/commands.

---

### **A. Core Features**
| Feature               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **Snippet Management** | Save prompts, commands, and image editing instructions.                    |
| **Categorization**     | Organize snippets into folders (e.g., "Portraits", "Product Photography"). |
| **Search**             | Full-text search across snippets.                                           |
| **Dynamic Variables**  | Use placeholders (e.g., `{outfit}`, `{background}`).                        |
| **Templates**          | Predefined templates (e.g., "Portrait Prompt", "Product Shot").         |
| **Cloud Sync**         | Optional cloud sync (e.g., Firebase, Supabase).                             |

---

### **B. Data Model**
```typescript
interface Snippet {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  variables?: Record<string, string>; // e.g., { "outfit": "Barbie Brat Chav" }
}
```

---

### **C. UI/UX Design**
1. **Button**:
   - 🧪 (lab beaker) next to "nudge" in the chat toolbar.

2. **Modal**:
   - **Sidebar**: Categories (e.g., "Portraits", "Backgrounds").
   - **Main Panel**: Snippet list (searchable, sortable).
   - **Preview Pane**: Shows snippet content.
   - **Action Buttons**: "Insert", "Edit", "Delete", "New".

---

### **D. Implementation**
#### **Frontend**
**Files**:
1. `webui/js/cmdlab.js`:
   - Logic for CmdLab modal and snippet management.
2. `webui/components/chat/toolbar.js`:
   - Add CmdLab button to the chat toolbar.

#### **Backend**
**Files**:
1. `backend/api/snippets.py`:
   - API endpoints for snippet storage (optional cloud sync).
2. `config/cmdlab_config.json`:
   - Default snippets and categories.

#### **Storage**
- **Default**: `localStorage` (with optional cloud sync).

---

### **E. Example Workflow**
1. **User Input**:
   ```text
   "change the setting to a scary terrifying forest bg scene and the outfit to a barbie brat chav"
   ```

2. **CmdLab Insertion**:
   - User clicks 🧪 and selects the "Portrait Prompt" template.
   - CmdLab inserts:
     ```text
     "A subject with a {background} background, wearing a {outfit}, editorial realism, ultra-realistic 8K resolution, hyper-detailed textures, cinematic lighting, shallow depth of field, captured on Sony A7R V, 50mm prime lens, f/2.0, ISO 200, 1/250."
     ```

3. **Dynamic Variables**:
   - User fills in:
     ```text
     {background} = "scary terrifying forest"
     {outfit} = "Barbie brat chav, tacky, cheap, skimpy, pink"
     ```

4. **Generated Prompt**:
   ```text
   "A subject with a scary terrifying forest background, wearing a Barbie brat chav outfit (tacky, cheap, skimpy, pink), editorial realism, ultra-realistic 8K resolution, hyper-detailed textures, cinematic lighting, shallow depth of field, captured on Sony A7R V, 50mm prime lens, f/2.0, ISO 200, 1/250."
   ```

---

## **3. Open Questions**
### **Seedream 4.5 Enhancements**
1. **Prompt Generation**:
   - Should we use **regex** or **NLP** for detecting modifications?
   - Should we **auto-detect** technical specs (e.g., "Sony A7R V")?

2. **`image_url` Resolution**:
   - What should the **fallback behavior** be if `SEEDREAM4_FILE_BASE_URL` is not configured?
   - Should we **validate** `remote_url` before using it as a fallback?

3. **Iterative Edits**:
   - Should we **cache** the entire `seedream4_result` or just the `image_url` and `prompt`?

4. **Performance**:
   - Should we **warn users** when selecting 4K resolution about slower generation times?

---

### **CmdLab Feature**
1. **Scope**:
   - Should snippets support **multi-image fusion** or **style transfer**?

2. **Dynamic Variables**:
   - Should placeholders (e.g., `{outfit}`) be **required** or **optional**?
   - Should we **auto-detect** variables from user input?

3. **Templates**:
   - Should we include **predefined templates**? If yes, what categories?

4. **Cloud Sync**:
   - Should cloud sync be **optional** or **required**?
   - If optional, what **default storage** should we use (`localStorage` or `IndexedDB`)?

5. **UI/UX**:
   - Should the CmdLab button be **always visible** or **context-aware**?
   - Should we include a **preview pane** for snippets?

6. **Local Server**:
   - Should we provide a **default configuration** for `SEEDREAM4_FILE_BASE_URL`?
   - Should we **auto-detect** the local server URL?
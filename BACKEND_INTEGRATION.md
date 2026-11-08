# Integration Checklist for Backend Developer

### 1. Image API Endpoint
* **Expects:** Form-data payload containing a medical scan file (`.png`, `.jpg`, or `.dcm`).
* **Returns:** JSON object containing class prediction confidence intervals and segmentation masks.

### 2. Live Chat Integration
* Target function: Update the `handleSendMessage` request hook in `src/App.jsx`.
* Switch out the native frontend `setTimeout` macro for a live `fetch` or `axios` POST route directing strings to the inference environment.

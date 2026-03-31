importScripts('config.js');

chrome.runtime.onInstalled.addListener(() => {
  console.log("Smart Job Auto-Filler installed.");
});

// Relay messages from content script to local API
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "LOGIN") {
    fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request.data)
    })
    .then(res => {
      if (!res.ok) throw new Error("Login failed");
      return res.json();
    })
    .then(data => {
      chrome.storage.local.set({ token: data.access_token }, () => {
        sendResponse({ success: true, user: data.user });
      });
    })
    .catch(err => sendResponse({ success: false, error: err.message }));
    return true;
  }

  if (request.type === "SAVE_FIELD" || request.type === "GET_FILL_VALUES" || request.type === "MATCH_FIELDS") {
    chrome.storage.local.get(['token'], (result) => {
      const token = result.token;
      if (!token) {
        sendResponse({ success: false, error: "Not logged in" });
        return;
      }

      const endpoint = request.type === "SAVE_FIELD" ? "save-field" : 
                       (request.type === "GET_FILL_VALUES" ? "get-fill-values" : "match-fields");
      const method = (request.type === "GET_FILL_VALUES") ? "GET" : "POST";
      
      const options = {
        method: method,
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      };
      if (method === "POST") options.body = JSON.stringify(request.data);

      fetch(`${CONFIG.API_BASE_URL}/${endpoint}`, options)
      .then(res => {
        if (res.status === 401) {
          chrome.storage.local.remove('token');
          throw new Error("Unauthorized");
        }
        return res.json();
      })
      .then(data => sendResponse({ success: true, data }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    });
    return true;
  }
});

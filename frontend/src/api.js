const API_BASE = "http://127.0.0.1:8000";

export const api = {
  // Analytics
  getAnalytics: async () => {
    const res = await fetch(`${API_BASE}/api/analytics`);
    return res.json();
  },

  // WooCommerce Sync
  syncWooCommerce: async () => {
    const res = await fetch(`${API_BASE}/api/sync`, { method: "POST" });
    return res.json();
  },

  // Customers
  getCustomers: async (search = "", tier = "") => {
    let url = `${API_BASE}/api/customers?limit=100`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (tier && tier !== "ALL") url += `&tier=${encodeURIComponent(tier)}`;
    const res = await fetch(url);
    return res.json();
  },

  getCustomerDetails: async (id) => {
    const res = await fetch(`${API_BASE}/api/customers/${id}`);
    return res.json();
  },

  updateCustomer: async (id, data) => {
    const res = await fetch(`${API_BASE}/api/customers/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  logCommunication: async (customerId, payload) => {
    const res = await fetch(`${API_BASE}/api/customers/${customerId}/communications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  // Orders
  getOrders: async (status = "") => {
    let url = `${API_BASE}/api/orders?limit=100`;
    if (status && status !== "ALL") url += `&status=${encodeURIComponent(status)}`;
    const res = await fetch(url);
    return res.json();
  },

  updateOrderStatus: async (orderId, newStatus) => {
    const res = await fetch(`${API_BASE}/api/orders/${orderId}/status?sync_to_wc=true`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    return res.json();
  },

  // Workflows
  getWorkflows: async () => {
    const res = await fetch(`${API_BASE}/api/workflows`);
    return res.json();
  },

  toggleWorkflow: async (id) => {
    const res = await fetch(`${API_BASE}/api/workflows/${id}/toggle`, { method: "POST" });
    return res.json();
  },

  getCommunications: async () => {
    const res = await fetch(`${API_BASE}/api/communications?limit=50`);
    return res.json();
  },

  // Simulator
  simulateWooCommerceOrder: async (amount = 2499.0) => {
    const res = await fetch(`${API_BASE}/api/webhooks/simulate?event_type=order.created&order_amount=${amount}`, {
      method: "POST",
    });
    return res.json();
  },

  // LLM & AI Agent Hooks
  getIncentivePolicies: async () => {
    const res = await fetch(`${API_BASE}/api/ai/incentive-policies`);
    return res.json();
  },

  aiDraftCommunication: async (customerId, intent = "festive_loyalty_offer", channel = "email", incentiveType = "auto") => {
    const res = await fetch(`${API_BASE}/api/ai/draft-communication?customer_id=${customerId}&intent=${encodeURIComponent(intent)}&channel=${encodeURIComponent(channel)}&incentive_type=${encodeURIComponent(incentiveType)}`, {
      method: "POST",
    });
    return res.json();
  },

  aiChurnRisk: async (customerId) => {
    const res = await fetch(`${API_BASE}/api/ai/churn-risk/${customerId}`);
    return res.json();
  },

  aiTriageNote: async (note) => {
    const res = await fetch(`${API_BASE}/api/ai/triage-note?note=${encodeURIComponent(note)}`, {
      method: "POST",
    });
    return res.json();
  },

  getSlippingCustomers: async () => {
    const res = await fetch(`${API_BASE}/api/ai/slipping-customers`);
    return res.json();
  },

  generateRetentionStrategy: async (customerId, incentiveType = "auto") => {
    const res = await fetch(`${API_BASE}/api/ai/retention-strategy/${customerId}?incentive_type=${encodeURIComponent(incentiveType)}`, {
      method: "POST",
    });
    return res.json();
  },

  triageHelpdeskTicket: async (customerId, subject, message) => {
    const res = await fetch(`${API_BASE}/api/ai/helpdesk-triage?customer_id=${customerId}&subject=${encodeURIComponent(subject)}&message=${encodeURIComponent(message)}`, {
      method: "POST",
    });
    return res.json();
  },

  runNaturalLanguageQuery: async (query) => {
    const res = await fetch(`${API_BASE}/api/ai/nl-query?query=${encodeURIComponent(query)}`, {
      method: "POST",
    });
    return res.json();
  },
};

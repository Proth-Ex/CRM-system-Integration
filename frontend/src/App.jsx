import React, { useState, useEffect } from "react";
import {
  Users,
  ShoppingBag,
  Zap,
  RefreshCw,
  Search,
  Mail,
  Phone,
  MessageSquare,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
  Tag,
  ShieldCheck,
  Send,
  X,
  Layers,
  ChevronRight,
  Sliders,
  Sparkles,
  Bot,
  BrainCircuit,
  MapPin,
  Cpu,
  Flame,
  Headphones,
  Check,
  HelpCircle,
  CornerDownRight
} from "lucide-react";
import { api } from "./api";
import {
  RevenueTrajectoryChart,
  RFMSegmentRingVisual,
  RegionalCitySpectrumVisual,
  OrderFulfillmentFunnelVisual,
  RetentionHealthGaugeVisual,
} from "./components/DashboardVisuals";

const INCENTIVE_OPTIONS = [
  {
    id: "free_delivery",
    icon: "🚚",
    label: "Free Delivery",
    sub: "Saves ₹150 delivery; 0% product price discount",
    code: "FREEDELIVERY",
    badge: "Margin Safe",
    color: "#38bdf8",
  },
  {
    id: "extended_warranty",
    icon: "🛡️",
    label: "6-Mo Warranty",
    sub: "CarePlus protection plan; ₹0 cash giveaway",
    code: "CAREPLUS",
    badge: "Zero Cash Hit",
    color: "#a855f7",
  },
  {
    id: "complimentary_gift",
    icon: "🎁",
    label: "Free Tech Gift",
    sub: "Braided cable / sample kit auto-added to cart",
    code: "FREEGIFT",
    badge: "Low Cost Gift",
    color: "#f59e0b",
  },
  {
    id: "capped_coupon",
    icon: "🏷️",
    label: "5% Capped Coupon",
    sub: "Strictly max ₹150 off; no hefty cuts",
    code: "SAVE5",
    badge: "Capped at ₹150",
    color: "#10b981",
  },
  {
    id: "vip_concierge",
    icon: "👑",
    label: "VIP Concierge",
    sub: "Store manager care & fast dispatch; ₹0 discount",
    code: "None",
    badge: "Zero Discount",
    color: "#ec4899",
  },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [analytics, setAnalytics] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [communications, setCommunications] = useState([]);
  const [slippingCustomers, setSlippingCustomers] = useState([]);
  
  // Filters & State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTier, setSelectedTier] = useState("ALL");
  const [selectedOrderStatus, setSelectedOrderStatus] = useState("ALL");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerModalData, setCustomerModalData] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [toast, setToast] = useState(null);

  // New Communication Form (Modal)
  const [commSubject, setCommSubject] = useState("");
  const [commContent, setCommContent] = useState("");
  const [commChannel, setCommChannel] = useState("email");
  const [isAIGenerating, setIsAIGenerating] = useState(false);

  // AI Retention Hub State
  const [retentionStrategies, setRetentionStrategies] = useState({});
  const [loadingRetentionId, setLoadingRetentionId] = useState(null);

  // Natural Language Search State
  const [nlQueryText, setNlQueryText] = useState("");
  const [isNlSearching, setIsNlSearching] = useState(false);
  const [nlSearchResult, setNlSearchResult] = useState(null);

  // Helpdesk Tickets State
  const [tickets, setTickets] = useState([
    {
      id: 101,
      customerId: 4,
      customerName: "Ananya Iyer",
      customerCity: "Chennai",
      subject: "Keychron K2 order stuck in pending for 5 days",
      message: "Hi support team, I placed an order for the Keychron mechanical keyboard 5 days ago and it is still showing 'Pending'. I have a major hackathon presentation this Friday in Chennai and need it delivered urgently. Can you please check why payment or dispatch is delayed?",
      triaged: null,
      status: "open",
    },
    {
      id: 102,
      customerId: 5,
      customerName: "Vikram Malhotra",
      customerCity: "New Delhi",
      subject: "Awaiting bank UTR clearance for Smart LED Lamp",
      message: "Hello, my order is on-hold for the Wipro smart plug and desk lamp. I initiated an IMPS wire transfer yesterday from my HDFC account. Can you verify if the reference cleared so you can ship to Hauz Khas?",
      triaged: null,
      status: "open",
    },
    {
      id: 103,
      customerId: 2,
      customerName: "Priya Patel",
      customerCity: "Panaji",
      subject: "Inquiring about extended warranty on boAt headphones",
      message: "Namaste team, my boAt Rockerz headphones just arrived at our Dona Paula office. The audio quality is fantastic! Do you offer a 1-year extended accidental protection plan?",
      triaged: null,
      status: "open",
    }
  ]);
  const [loadingTicketId, setLoadingTicketId] = useState(null);

  // AI Hub Interactive State
  const [aiSelectedCustomerId, setAiSelectedCustomerId] = useState("");
  const [aiIntent, setAiIntent] = useState("festive_loyalty_offer");
  const [aiResult, setAiResult] = useState(null);
  const [aiChurnResult, setAiChurnResult] = useState(null);
  const [aiTestNote, setAiTestNote] = useState("Urgent delivery required for wedding reception at Taj Panaji! Please call security desk on arrival.");
  const [aiTriageResult, setAiTriageResult] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadAllData = async () => {
    try {
      const [analyticsData, custData, ordData, wfData, commData, slipData] = await Promise.all([
        api.getAnalytics(),
        api.getCustomers(searchQuery, selectedTier),
        api.getOrders(selectedOrderStatus),
        api.getWorkflows(),
        api.getCommunications(),
        api.getSlippingCustomers(),
      ]);
      setAnalytics(analyticsData);
      setCustomers(custData);
      setOrders(ordData);
      setWorkflows(wfData);
      setCommunications(commData);
      setSlippingCustomers(slipData);
      if (custData.length > 0 && !aiSelectedCustomerId) {
        setAiSelectedCustomerId(custData[0].id.toString());
      }
    } catch (err) {
      console.error("Error loading CRM data:", err);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [searchQuery, selectedTier, selectedOrderStatus]);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const res = await api.syncWooCommerce();
      showToast(`WooCommerce Synced: ${res.details.synced_customers} Indian customers, ${res.details.synced_orders} orders!`);
      await loadAllData();
    } catch (err) {
      showToast("Sync failed. Check WooCommerce connection.", "error");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleSimulateOrder = async (amount = 8499.0) => {
    setIsSimulating(true);
    try {
      const res = await api.simulateWooCommerceOrder(amount);
      showToast(`Simulated Order #${res.wc_order_id} placed for ${res.customer_email}! Automated workflows triggered.`);
      await loadAllData();
    } catch (err) {
      showToast("Simulation failed", "error");
    } finally {
      setIsSimulating(false);
    }
  };

  const openCustomerDetails = async (cust) => {
    setCommSubject("");
    setCommContent("");
    setCommChannel("email");
    try {
      const fullData = await api.getCustomerDetails(cust.id);
      setSelectedCustomer(cust);
      setCustomerModalData(fullData);
    } catch (err) {
      showToast("Failed to fetch customer 360 profile", "error");
    }
  };

  const handleAIDraftInModal = async () => {
    if (!selectedCustomer) return;
    setIsAIGenerating(true);
    try {
      const draft = await api.aiDraftCommunication(
        selectedCustomer.id,
        "festive_loyalty_offer",
        commChannel,
        "auto"
      );
      setCommSubject(draft.generated_subject);
      setCommContent(draft.generated_body);
      showToast(`✨ Gemini selected ${draft.incentive_label || "offer"} based on customer history!`);
    } catch (err) {
      showToast("AI generation error", "error");
    } finally {
      setIsAIGenerating(false);
    }
  };

  const handleGenerateRetention = async (customerId) => {
    setLoadingRetentionId(customerId);
    try {
      const strategy = await api.generateRetentionStrategy(customerId, "auto");
      setRetentionStrategies((prev) => ({
        ...prev,
        [customerId]: strategy,
      }));
      showToast(`✨ Gemini autonomously selected ${strategy.incentive_label || "offer"} for ${strategy.customer_name}!`);
    } catch (err) {
      showToast("Failed to generate retention strategy", "error");
    } finally {
      setLoadingRetentionId(null);
    }
  };

  // Run AI Ticket Resolution & Helpdesk Triage
  const handleTriageTicket = async (ticket) => {
    setLoadingTicketId(ticket.id);
    try {
      const result = await api.triageHelpdeskTicket(ticket.customerId, ticket.subject, ticket.message);
      setTickets((prev) =>
        prev.map((t) => (t.id === ticket.id ? { ...t, triaged: result } : t))
      );
      showToast(`✨ Gemini classified ticket sentiment (${result.sentiment}) and generated Co-pilot draft!`);
    } catch (err) {
      showToast("Helpdesk AI triage failed", "error");
    } finally {
      setLoadingTicketId(null);
    }
  };

  const handleDispatchTicketReply = async (ticket) => {
    if (!ticket.triaged?.agent_copilot_reply) return;
    try {
      await api.logCommunication(ticket.customerId, {
        customer_id: ticket.customerId,
        channel: "email",
        direction: "outbound",
        subject: `Re: ${ticket.subject}`,
        content: ticket.triaged.agent_copilot_reply,
        status: "sent",
        trigger_source: "helpdesk_ai_copilot",
      });
      setTickets((prev) =>
        prev.map((t) => (t.id === ticket.id ? { ...t, status: "resolved" } : t))
      );
      showToast(`Resolution reply dispatched to ${ticket.customerName}! Ticket marked Resolved.`);
      loadAllData();
    } catch (err) {
      showToast("Failed to dispatch reply", "error");
    }
  };

  // Run Natural Language CRM Search
  const handleRunNLSearch = async (e) => {
    e?.preventDefault();
    if (!nlQueryText.trim()) return;
    setIsNlSearching(true);
    try {
      const res = await api.runNaturalLanguageQuery(nlQueryText);
      setNlSearchResult(res);
      showToast(`Copilot matched ${res.matched_count} customers!`);
    } catch (err) {
      showToast("Natural language search failed", "error");
    } finally {
      setIsNlSearching(false);
    }
  };

  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      await api.updateOrderStatus(orderId, newStatus);
      showToast(`Order updated to '${newStatus}' & synced to WooCommerce!`);
      await loadAllData();
      if (selectedCustomer) {
        openCustomerDetails(selectedCustomer);
      }
    } catch (err) {
      showToast("Failed to update status", "error");
    }
  };

  const handleSendCommunication = async (e) => {
    e.preventDefault();
    if (!commContent || !selectedCustomer) return;
    try {
      await api.logCommunication(selectedCustomer.id, {
        customer_id: selectedCustomer.id,
        channel: commChannel,
        direction: "outbound",
        subject: commSubject || `${commChannel.toUpperCase()} from KILOWOTT Support`,
        content: commContent,
        status: "sent",
        trigger_source: "manual",
      });
      showToast(`Communication dispatched to ${selectedCustomer.email}!`);
      setCommSubject("");
      setCommContent("");
      openCustomerDetails(selectedCustomer);
      loadAllData();
    } catch (err) {
      showToast("Failed to dispatch communication", "error");
    }
  };

  const handleToggleWorkflow = async (wfId) => {
    try {
      const updated = await api.toggleWorkflow(wfId);
      showToast(`Workflow '${updated.name}' is now ${updated.is_active ? "Active" : "Paused"}`);
      const wfData = await api.getWorkflows();
      setWorkflows(wfData);
    } catch (err) {
      showToast("Failed to toggle workflow", "error");
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "var(--bg-main)" }}>
      {/* Toast Notification */}
      {toast && (
        <div
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            zIndex: 9999,
            backgroundColor: toast.type === "error" ? "rgba(244, 63, 94, 0.95)" : "rgba(16, 185, 129, 0.95)",
            color: "#ffffff",
            padding: "12px 20px",
            borderRadius: "var(--radius-md)",
            boxShadow: "0 8px 30px rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "0.88rem",
            fontWeight: 600,
            animation: "fadeIn 0.2s ease",
          }}
        >
          {toast.type === "error" ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
          {toast.message}
        </div>
      )}

      {/* Sidebar */}
      <aside
        style={{
          width: "270px",
          backgroundColor: "var(--bg-sidebar)",
          borderRight: "1px solid var(--border-subtle)",
          padding: "24px 16px",
          display: "flex",
          flexDirection: "column",
          gap: "24px",
        }}
      >
        {/* Brand */}
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                color: "#fff",
                fontSize: "1.1rem",
              }}
            >
              K
            </div>
            <div>
              <h2 style={{ fontSize: "1.05rem", fontWeight: 700, letterSpacing: "-0.01em" }}>KILOWOTT CRM</h2>
              <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>India WooCommerce Suite</p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {[
            { id: "dashboard", label: "Dashboard Overview", icon: <TrendingUp size={18} /> },
            { id: "helpdesk", label: "Helpdesk & Tickets (AI)", icon: <Headphones size={18} color="#06b6d4" /> },
            { id: "retention", label: "Slipping Customers (AI)", icon: <Flame size={18} color="#f43f5e" /> },
            { id: "customers", label: "Customer 360° (India)", icon: <Users size={18} /> },
            { id: "orders", label: "Order Tracking", icon: <ShoppingBag size={18} /> },
            { id: "workflows", label: "Automated Workflows", icon: <Zap size={18} /> },
            { id: "ai_hub", label: "Gemini AI Hub", icon: <Sparkles size={18} color="#c084fc" /> },
            { id: "communications", label: "Communication Logs", icon: <MessageSquare size={18} /> },
          ].map((item) => {
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  backgroundColor: active ? "var(--primary-glow)" : "transparent",
                  color: active ? "#818cf8" : "var(--text-secondary)",
                  fontWeight: active ? 600 : 500,
                  fontSize: "0.88rem",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.15s ease",
                  borderLeft: active ? "3px solid var(--primary)" : "3px solid transparent",
                }}
              >
                {item.icon}
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Gemini Active Badge */}
        <div
          style={{
            marginTop: "auto",
            padding: "14px",
            backgroundColor: "var(--bg-card)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: "var(--accent-emerald)",
                boxShadow: "0 0 8px var(--accent-emerald)",
              }}
            />
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-emerald)" }}>
              Google Gemini Live
            </span>
          </div>
          <p style={{ fontSize: "0.72rem", color: "var(--text-muted)", lineHeight: "1.4" }}>
            Model: <strong style={{ color: "var(--text-secondary)" }}>gemini-3.5-flash-lite</strong>
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflowY: "auto", padding: "28px 36px" }}>
        {/* Top Header with Natural Language Copilot Search */}
        <div style={{ marginBottom: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
            <div>
              <h1 style={{ fontSize: "1.65rem", fontWeight: 700, color: "var(--text-primary)" }}>
                {activeTab === "dashboard" && "Executive Dashboard"}
                {activeTab === "helpdesk" && "AI Support & Helpdesk Ticket Resolution"}
                {activeTab === "retention" && "Slipping Customers & AI Retention Radar"}
                {activeTab === "customers" && "Customer 360° Management"}
                {activeTab === "orders" && "WooCommerce Order Tracking Pipeline"}
                {activeTab === "workflows" && "Automated Communication Workflows"}
                {activeTab === "ai_hub" && "Google Gemini AI Deployment Hub"}
                {activeTab === "communications" && "Dispatched Communication Logs"}
              </h1>
              <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                WooCommerce REST v3 Integration Suite • Google Gemini Live Connected
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                onClick={handleSync}
                disabled={isSyncing}
                className="btn btn-secondary"
                style={{ fontSize: "0.84rem" }}
              >
                <RefreshCw size={15} className={isSyncing ? "pulse-glow" : ""} />
                {isSyncing ? "Syncing..." : "Sync WooCommerce"}
              </button>

              <button
                onClick={() => handleSimulateOrder(8499.0)}
                disabled={isSimulating}
                className="btn btn-primary"
                style={{ fontSize: "0.84rem" }}
              >
                <Zap size={15} />
                {isSimulating ? "Simulating..." : "Simulate WC Order (₹)"}
              </button>
            </div>
          </div>

          {/* ITEM 4: Natural Language Database Search Bar */}
          <form
            onSubmit={handleRunNLSearch}
            className="glass-panel"
            style={{
              padding: "10px 16px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              background: "linear-gradient(135deg, rgba(20, 24, 36, 0.9), rgba(99, 102, 241, 0.12))",
            }}
          >
            <Bot size={20} color="#818cf8" />
            <input
              type="text"
              placeholder="Ask CRM Copilot in plain English: 'Which customers in Bengaluru spent over 20000?' or 'Show VIP customers'..."
              value={nlQueryText}
              onChange={(e) => setNlQueryText(e.target.value)}
              style={{ flex: 1, backgroundColor: "transparent", border: "none", outline: "none", fontSize: "0.88rem" }}
            />
            <button
              type="submit"
              disabled={isNlSearching}
              className="btn btn-primary btn-sm"
              style={{ padding: "6px 14px" }}
            >
              <Sparkles size={14} /> {isNlSearching ? "Thinking..." : "Ask Copilot"}
            </button>
          </form>

          {/* Natural Language Query Result Dropdown */}
          {nlSearchResult && (
            <div
              className="glass-panel animate-fade-in"
              style={{
                marginTop: "10px",
                padding: "16px 20px",
                border: "1px solid rgba(99, 102, 241, 0.4)",
                display: "flex",
                flexDirection: "column",
                gap: "10px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.85rem", color: "#818cf8", fontWeight: 700 }}>
                  🔍 Copilot Interpretation: {nlSearchResult.explanation}
                </span>
                <button
                  onClick={() => setNlSearchResult(null)}
                  style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                >
                  <X size={16} />
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "10px" }}>
                {nlSearchResult.results?.map((res) => (
                  <div
                    key={res.id}
                    onClick={() => {
                      const c = customers.find((cust) => cust.id === res.id);
                      if (c) openCustomerDetails(c);
                    }}
                    style={{
                      padding: "10px 14px",
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: "var(--radius-sm)",
                      cursor: "pointer",
                      fontSize: "0.82rem",
                    }}
                  >
                    <strong>{res.name}</strong> ({res.city})
                    <div style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>
                      LTV: ₹{Number(res.total_spent).toLocaleString('en-IN')} • {res.tier} Tier
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* TAB 1: HELPDESK & TICKETS (AI) - DIRECT MATCH TO SLIDE 1! */}
        {activeTab === "helpdesk" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div
              className="glass-panel"
              style={{
                padding: "22px",
                background: "linear-gradient(135deg, rgba(20, 24, 36, 0.95), rgba(6, 182, 212, 0.15))",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "14px",
              }}
            >
              <div>
                <h2 style={{ fontSize: "1.3rem", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Headphones size={22} color="#06b6d4" />
                  Automated Support & Helpdesk Ticket Resolution
                </h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "4px" }}>
                  Context-Aware Deflection, Sentiment & Urgency Triage, 2-Sentence Briefs, and One-Click Agent Co-pilot.
                </p>
              </div>
              <span className="badge badge-loyal">Powered by Google Gemini</span>
            </div>

            {/* Tickets List */}
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {tickets.map((t) => {
                const isLoading = loadingTicketId === t.id;
                const triaged = t.triaged;

                return (
                  <div key={t.id} className="glass-card" style={{ padding: "22px", display: "flex", flexDirection: "column", gap: "14px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                          <span style={{ fontFamily: "var(--font-mono)", color: "var(--primary)", fontWeight: 700 }}>
                            #{t.id}
                          </span>
                          <h3 style={{ fontSize: "1.05rem" }}>{t.subject}</h3>
                          <span className={`badge ${t.status === 'resolved' ? 'badge-completed' : 'badge-pending'}`}>
                            {t.status}
                          </span>
                        </div>
                        <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                          Customer: <strong>{t.customerName}</strong> ({t.customerCity})
                        </p>
                      </div>

                      <div style={{ display: "flex", gap: "8px" }}>
                        {!triaged ? (
                          <button
                            onClick={() => handleTriageTicket(t)}
                            disabled={isLoading}
                            className="btn btn-primary btn-sm"
                          >
                            <Sparkles size={14} /> {isLoading ? "Gemini Triaging..." : "🤖 Run AI Triage & Co-pilot"}
                          </button>
                        ) : (
                          <button
                            onClick={() => handleTriageTicket(t)}
                            disabled={isLoading}
                            className="btn btn-secondary btn-sm"
                          >
                            <RefreshCw size={13} /> Re-analyze
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Original Message */}
                    <div
                      style={{
                        padding: "12px 16px",
                        backgroundColor: "var(--bg-surface)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "0.85rem",
                        color: "var(--text-secondary)",
                        borderLeft: "3px solid var(--border-subtle)",
                      }}
                    >
                      "{t.message}"
                    </div>

                    {/* AI Triaged Intelligence Card */}
                    {triaged && (
                      <div
                        className="animate-fade-in"
                        style={{
                          padding: "16px 20px",
                          backgroundColor: "rgba(6, 182, 212, 0.08)",
                          border: "1px solid rgba(6, 182, 212, 0.3)",
                          borderRadius: "var(--radius-md)",
                          display: "flex",
                          flexDirection: "column",
                          gap: "10px",
                        }}
                      >
                        {/* Sentiment & Urgency Badges */}
                        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                          <span className={`badge ${triaged.sentiment === 'Frustrated' ? 'badge-cancelled' : 'badge-loyal'}`}>
                            Sentiment: {triaged.sentiment}
                          </span>
                          <span className={`badge ${triaged.urgency === 'High' ? 'badge-cancelled' : 'badge-regular'}`}>
                            Urgency: {triaged.urgency}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginLeft: "auto" }}>
                            {triaged.model}
                          </span>
                        </div>

                        {/* 2-Sentence Ticket Summary */}
                        <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                          <strong>📄 2-Sentence Ticket Brief:</strong> {triaged.two_sentence_summary}
                        </div>

                        {/* One-Click Agent Co-pilot Draft */}
                        <div style={{ fontSize: "0.82rem", marginTop: "4px" }}>
                          <strong style={{ color: "#22d3ee", display: "flex", alignItems: "center", gap: "6px" }}>
                            <Bot size={15} /> One-Click Agent Co-pilot Resolution Draft:
                          </strong>
                          <div
                            style={{
                              marginTop: "6px",
                              padding: "12px",
                              backgroundColor: "var(--bg-surface)",
                              borderRadius: "var(--radius-sm)",
                              fontSize: "0.8rem",
                              whiteSpace: "pre-wrap",
                              fontFamily: "var(--font-mono)",
                              color: "var(--text-primary)",
                            }}
                          >
                            {triaged.agent_copilot_reply}
                          </div>
                        </div>

                        {/* Action: Send Resolution */}
                        {t.status !== "resolved" && (
                          <button
                            onClick={() => handleDispatchTicketReply(t)}
                            className="btn btn-primary btn-sm"
                            style={{ alignSelf: "flex-start", marginTop: "6px" }}
                          >
                            <Send size={13} /> 1-Click Send Resolution to {t.customerName}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 2: SLIPPING CUSTOMERS & AI RETENTION RADAR - MATCH TO SLIDE 2! */}
        {activeTab === "retention" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div
              className="glass-panel"
              style={{
                padding: "22px",
                background: "linear-gradient(135deg, rgba(20, 24, 36, 0.95), rgba(244, 63, 94, 0.15))",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "14px",
              }}
            >
              <div>
                <h2 style={{ fontSize: "1.3rem", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Flame size={22} color="#f43f5e" />
                  Dynamic Churn Intervention & Retention Marketing
                </h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "4px" }}>
                  Detects behavioral warning signs and uses Live Gemini to draft tailored win-back offers.
                </p>
              </div>
              <span className="badge badge-vip">Gemini Live Connected</span>
            </div>

            {/* Autonomous Context-Aware Policy Banner */}
            <div
              className="glass-panel"
              style={{
                padding: "16px 20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "12px",
                border: "1px solid rgba(56, 189, 248, 0.3)",
                background: "linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(56, 189, 248, 0.08))",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <ShieldCheck size={20} color="#38bdf8" />
                <div>
                  <div style={{ fontSize: "0.92rem", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
                    Autonomous Context-Aware Win-Back Engine
                    <span
                      style={{
                        fontSize: "0.7rem",
                        padding: "2px 8px",
                        borderRadius: "12px",
                        backgroundColor: "rgba(16, 185, 129, 0.15)",
                        color: "#34d399",
                        border: "1px solid rgba(16, 185, 129, 0.3)",
                        fontWeight: 600,
                      }}
                    >
                      Zero Margin Leaks
                    </span>
                  </div>
                  <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", margin: "2px 0 0" }}>
                    Gemini autonomously analyzes each customer's past items, LTV, and churn pattern to choose the optimal margin-safe offer — zero manual guessing, zero hefty discount giveaways.
                  </p>
                </div>
              </div>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {INCENTIVE_OPTIONS.map((opt) => (
                  <span
                    key={opt.id}
                    style={{
                      fontSize: "0.72rem",
                      padding: "3px 8px",
                      borderRadius: "6px",
                      backgroundColor: "rgba(255, 255, 255, 0.05)",
                      color: opt.color,
                      border: "1px solid var(--border-subtle)",
                      fontWeight: 600,
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    {opt.icon} {opt.label}
                  </span>
                ))}
              </div>
            </div>

            {/* List of Slipping Customers */}
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {slippingCustomers.map((cust) => {
                const strat = retentionStrategies[cust.customer_id];
                const isLoading = loadingRetentionId === cust.customer_id;

                return (
                  <div key={cust.customer_id} className="glass-card" style={{ padding: "22px", display: "flex", flexDirection: "column", gap: "14px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
                      <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
                        <div
                          style={{
                            width: "44px",
                            height: "44px",
                            borderRadius: "50%",
                            background: cust.risk_level === "HIGH RISK" ? "rgba(244, 63, 94, 0.2)" : "rgba(245, 158, 11, 0.2)",
                            color: cust.risk_level === "HIGH RISK" ? "#fb7185" : "#fbbf24",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontWeight: 700,
                          }}
                        >
                          {cust.name[0]}
                        </div>
                        <div>
                          <h3 style={{ fontSize: "1.05rem" }}>{cust.name}</h3>
                          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                            {cust.email} • {cust.city} • LTV: <strong>₹{Number(cust.total_spent).toLocaleString('en-IN')}</strong> ({cust.orders_count} orders)
                          </p>
                        </div>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span className={`badge badge-${cust.risk_level === "HIGH RISK" ? "cancelled" : "pending"}`}>
                          {cust.slip_probability}% Slip Probability ({cust.risk_level})
                        </span>
                        <button
                          onClick={() => handleGenerateRetention(cust.customer_id)}
                          disabled={isLoading}
                          className="btn btn-primary btn-sm"
                        >
                          <Sparkles size={14} /> {isLoading ? "Gemini Evaluating Context..." : "🤖 Generate Contextual Win-Back Plan"}
                        </button>
                      </div>
                    </div>

                    {/* Behavioral Triggers */}
                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                      {cust.behavioral_triggers.map((trig, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: "4px 10px",
                            backgroundColor: "var(--bg-surface)",
                            borderRadius: "var(--radius-sm)",
                            fontSize: "0.76rem",
                            color: "#cbd5e1",
                            border: "1px solid var(--border-subtle)",
                          }}
                        >
                          ⚠️ {trig}
                        </span>
                      ))}
                    </div>

                    {/* AI Generated Retention Strategy Card */}
                    {strat && (
                      <div
                        className="animate-fade-in"
                        style={{
                          padding: "16px 20px",
                          backgroundColor: "rgba(99, 102, 241, 0.08)",
                          border: "1px solid rgba(99, 102, 241, 0.3)",
                          borderRadius: "var(--radius-md)",
                          display: "flex",
                          flexDirection: "column",
                          gap: "10px",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                          <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#818cf8", display: "flex", alignItems: "center", gap: "6px" }}>
                            <Bot size={16} /> Gemini Autonomous Retention Strategy
                          </span>
                          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                            <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "10px", backgroundColor: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid rgba(56, 189, 248, 0.3)", fontWeight: 600 }}>
                              ✨ AI Selected: {strat.incentive_label || "Free Delivery"} {strat.incentive_code ? `(${strat.incentive_code})` : ""}
                            </span>
                            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{strat.model}</span>
                          </div>
                        </div>

                        {strat.incentive_rationale && (
                          <div style={{ fontSize: "0.82rem", color: "#38bdf8", backgroundColor: "rgba(56, 189, 248, 0.08)", padding: "8px 12px", borderRadius: "var(--radius-sm)", border: "1px solid rgba(56, 189, 248, 0.2)" }}>
                            <strong>🧠 AI Context Rationale:</strong> {strat.incentive_rationale}
                          </div>
                        )}

                        <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                          <strong>Behavioral Diagnosis:</strong> {strat.behavioral_diagnosis}
                        </div>

                        <div style={{ fontSize: "0.82rem", color: "var(--accent-emerald)" }}>
                          <strong>Recommended Retention Action:</strong> {strat.retention_action}
                        </div>

                        <div
                          style={{
                            padding: "12px",
                            backgroundColor: "var(--bg-surface)",
                            borderRadius: "var(--radius-sm)",
                            fontSize: "0.8rem",
                            whiteSpace: "pre-wrap",
                            fontFamily: "var(--font-mono)",
                            color: "var(--text-primary)",
                          }}
                        >
                          {strat.recovery_message}
                        </div>

                        <button
                          onClick={() => {
                            const c = customers.find((custo) => custo.id === cust.customer_id);
                            if (c) {
                              openCustomerDetails(c);
                              setCommSubject(`Exclusive Retention Benefit for ${strat.customer_name}`);
                              setCommContent(strat.recovery_message);
                            }
                          }}
                          className="btn btn-secondary btn-sm"
                          style={{ alignSelf: "flex-start", color: "#818cf8", borderColor: "rgba(99, 102, 241, 0.4)" }}
                        >
                          <Send size={13} /> Open in Communication Composer & Dispatch →
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 3: DASHBOARD */}
        {activeTab === "dashboard" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {/* KPI Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
              <div className="glass-card" style={{ padding: "20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Total Revenue (LTV)</span>
                  <span style={{ color: "var(--accent-emerald)", fontWeight: 800 }}>₹ INR</span>
                </div>
                <div style={{ fontSize: "1.85rem", fontWeight: 700, marginTop: "8px", fontFamily: "var(--font-mono)" }}>
                  ₹{analytics?.total_revenue ? Number(analytics.total_revenue).toLocaleString('en-IN') : "0"}
                </div>
                <div style={{ fontSize: "0.76rem", color: "var(--accent-emerald)", marginTop: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
                  <ArrowUpRight size={14} /> Synced from completed orders
                </div>
              </div>

              <div className="glass-card" style={{ padding: "20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Total Customers</span>
                  <Users size={20} color="var(--primary)" />
                </div>
                <div style={{ fontSize: "1.85rem", fontWeight: 700, marginTop: "8px", fontFamily: "var(--font-mono)" }}>
                  {analytics?.total_customers || 0}
                </div>
                <div style={{ fontSize: "0.76rem", color: "var(--text-secondary)", marginTop: "6px" }}>
                  Bengaluru, Goa, Mumbai, Chennai, Delhi
                </div>
              </div>

              <div className="glass-card" style={{ padding: "20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Open Support Tickets</span>
                  <Headphones size={20} color="var(--accent-cyan)" />
                </div>
                <div style={{ fontSize: "1.85rem", fontWeight: 700, marginTop: "8px", fontFamily: "var(--font-mono)" }}>
                  {tickets.filter((t) => t.status === "open").length} Open
                </div>
                <div style={{ fontSize: "0.76rem", color: "var(--accent-cyan)", marginTop: "6px" }}>
                  AI Co-pilot Deflection Ready
                </div>
              </div>

              <div className="glass-card" style={{ padding: "20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>High Churn Alert</span>
                  <Flame size={20} color="var(--accent-rose)" />
                </div>
                <div style={{ fontSize: "1.85rem", fontWeight: 700, marginTop: "8px", fontFamily: "var(--font-mono)", color: "var(--accent-rose)" }}>
                  {slippingCustomers.filter((c) => c.risk_level === "HIGH RISK").length} High Risk
                </div>
                <div style={{ fontSize: "0.76rem", color: "var(--accent-rose)", marginTop: "6px" }}>
                  Requires automated retention action
                </div>
              </div>
            </div>

            {/* Visual Analytics Row 1: Revenue Trajectory + RFM Segments */}
            <div className="dashboard-grid-2-1">
              <RevenueTrajectoryChart orders={orders} totalRevenue={analytics?.total_revenue} />
              <RFMSegmentRingVisual customers={customers} tierDistribution={analytics?.tier_distribution} />
            </div>

            {/* Visual Analytics Row 2: Regional Order Spectrum + Order Fulfillment Funnel */}
            <div className="dashboard-grid-1-1">
              <RegionalCitySpectrumVisual customers={customers} orders={orders} />
              <OrderFulfillmentFunnelVisual orders={orders} />
            </div>

            {/* Visual Analytics Row 3: Retention Health & Churn Probability Gauge */}
            <RetentionHealthGaugeVisual slippingCustomers={slippingCustomers} />

            {/* Quick Navigation Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div className="glass-card" style={{ padding: "22px" }}>
                <h3 style={{ fontSize: "1.05rem", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Headphones size={18} color="var(--accent-cyan)" />
                  Automated Support Helpdesk
                </h3>
                <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "16px" }}>
                  Context-aware ticket deflection and 1-click empathetic resolution replies generated using customer order context.
                </p>
                <button
                  onClick={() => setActiveTab("helpdesk")}
                  className="btn btn-secondary"
                  style={{ width: "100%", justifyContent: "flex-start" }}
                >
                  Open AI Helpdesk & Tickets Queue →
                </button>
              </div>

              <div className="glass-card" style={{ padding: "22px" }}>
                <h3 style={{ fontSize: "1.05rem", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Flame size={18} color="var(--accent-rose)" />
                  Dynamic Churn Intervention Radar
                </h3>
                <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "16px" }}>
                  Identifies customers about to slip and uses Google Gemini to generate tailored win-back recovery copy.
                </p>
                <button
                  onClick={() => setActiveTab("retention")}
                  className="btn btn-secondary"
                  style={{ width: "100%", justifyContent: "flex-start" }}
                >
                  Open Slipping Customers Radar →
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: CUSTOMERS 360° */}
        {activeTab === "customers" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{ display: "flex", gap: "14px", flexWrap: "wrap", alignItems: "center" }}>
              <div style={{ position: "relative", flex: 1, minWidth: "260px" }}>
                <Search size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input
                  type="text"
                  placeholder="Search by Indian name, email, or city..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ width: "100%", paddingLeft: "36px" }}
                />
              </div>

              <div style={{ display: "flex", gap: "6px" }}>
                {["ALL", "VIP", "Loyal", "New", "Regular"].map((tier) => (
                  <button
                    key={tier}
                    onClick={() => setSelectedTier(tier)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: "var(--radius-full)",
                      fontSize: "0.78rem",
                      fontWeight: 600,
                      border: "none",
                      cursor: "pointer",
                      backgroundColor: selectedTier === tier ? "var(--primary)" : "var(--bg-surface)",
                      color: selectedTier === tier ? "#fff" : "var(--text-secondary)",
                    }}
                  >
                    {tier}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
              {customers.map((cust) => (
                <div
                  key={cust.id}
                  onClick={() => openCustomerDetails(cust)}
                  className="glass-card"
                  style={{ padding: "20px", cursor: "pointer", display: "flex", flexDirection: "column", gap: "14px" }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                      <div
                        style={{
                          width: "44px",
                          height: "44px",
                          borderRadius: "50%",
                          background: "linear-gradient(135deg, #4f46e5, #06b6d4)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontWeight: 700,
                          fontSize: "1rem",
                        }}
                      >
                        {cust.first_name?.[0] || cust.email[0]?.toUpperCase()}
                      </div>
                      <div>
                        <h4 style={{ fontSize: "0.96rem" }}>
                          {cust.first_name || cust.last_name ? `${cust.first_name} ${cust.last_name}` : cust.email.split("@")[0]}
                        </h4>
                        <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
                          <MapPin size={12} /> {cust.billing_address?.city || "India"} • {cust.email}
                        </p>
                      </div>
                    </div>
                    <span className={`badge badge-${cust.tier.toLowerCase()}`}>{cust.tier}</span>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr 1fr",
                      padding: "10px",
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: "var(--radius-sm)",
                      textAlign: "center",
                    }}
                  >
                    <div>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Total LTV</span>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--accent-emerald)" }}>
                        ₹{Number(cust.total_spent).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </div>
                    </div>
                    <div>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Orders</span>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                        {cust.orders_count}
                      </div>
                    </div>
                    <div>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>AOV</span>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                        ₹{Number(cust.avg_order_value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.76rem", color: "var(--text-muted)" }}>
                    <span>Phone: {cust.phone || "+91 Mobile"}</span>
                    <span style={{ color: "#818cf8", fontWeight: 600 }}>Open 360° Profile →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: ORDERS */}
        {activeTab === "orders" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "4px" }}>
              {["ALL", "pending", "processing", "on-hold", "completed", "cancelled"].map((st) => (
                <button
                  key={st}
                  onClick={() => setSelectedOrderStatus(st)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    border: "none",
                    cursor: "pointer",
                    textTransform: "capitalize",
                    backgroundColor: selectedOrderStatus === st ? "var(--primary)" : "var(--bg-card)",
                    color: selectedOrderStatus === st ? "#fff" : "var(--text-secondary)",
                  }}
                >
                  {st}
                </button>
              ))}
            </div>

            <div className="glass-panel" style={{ overflow: "hidden" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.88rem" }}>
                <thead>
                  <tr style={{ backgroundColor: "var(--bg-surface)", borderBottom: "1px solid var(--border-subtle)", color: "var(--text-muted)", fontSize: "0.78rem" }}>
                    <th style={{ padding: "14px 20px" }}>ORDER</th>
                    <th style={{ padding: "14px 20px" }}>CUSTOMER & CITY</th>
                    <th style={{ padding: "14px 20px" }}>LINE ITEMS</th>
                    <th style={{ padding: "14px 20px" }}>AMOUNT (INR)</th>
                    <th style={{ padding: "14px 20px" }}>STATUS</th>
                    <th style={{ padding: "14px 20px" }}>ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr
                      key={o.id}
                      style={{ borderBottom: "1px solid var(--border-subtle)", transition: "background 0.15s" }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.02)")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                    >
                      <td style={{ padding: "14px 20px", fontFamily: "var(--font-mono)", fontWeight: 700, color: "var(--primary)" }}>
                        #{o.wc_order_id}
                      </td>
                      <td style={{ padding: "14px 20px" }}>
                        <div style={{ fontWeight: 600 }}>{o.customer_email}</div>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                          {o.billing?.city || "India"} • {o.payment_method}
                        </div>
                      </td>
                      <td style={{ padding: "14px 20px" }}>
                        <div style={{ fontSize: "0.82rem" }}>
                          {o.line_items?.map((item, idx) => (
                            <div key={idx} style={{ color: "var(--text-secondary)" }}>
                              • {item.name} × {item.quantity}
                            </div>
                          ))}
                        </div>
                      </td>
                      <td style={{ padding: "14px 20px", fontFamily: "var(--font-mono)", fontWeight: 700, color: "var(--accent-emerald)" }}>
                        ₹{Number(o.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: "14px 20px" }}>
                        <span className={`badge badge-${o.status}`}>{o.status}</span>
                      </td>
                      <td style={{ padding: "14px 20px" }}>
                        <select
                          value={o.status}
                          onChange={(e) => handleUpdateOrderStatus(o.id, e.target.value)}
                          style={{ padding: "4px 8px", fontSize: "0.8rem", cursor: "pointer" }}
                        >
                          <option value="pending">Pending</option>
                          <option value="processing">Processing</option>
                          <option value="on-hold">On-Hold</option>
                          <option value="completed">Completed</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 6: WORKFLOWS */}
        {activeTab === "workflows" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "16px" }}>
              {workflows.map((wf) => (
                <div key={wf.id} className="glass-card" style={{ padding: "22px", display: "flex", flexDirection: "column", gap: "14px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <h3 style={{ fontSize: "1.05rem" }}>{wf.name}</h3>
                      <span className="badge badge-loyal" style={{ marginTop: "6px" }}>
                        Trigger: {wf.trigger_event}
                      </span>
                    </div>
                    <button
                      onClick={() => handleToggleWorkflow(wf.id)}
                      className={`btn btn-sm ${wf.is_active ? "btn-primary" : "btn-secondary"}`}
                    >
                      {wf.is_active ? "Active" : "Paused"}
                    </button>
                  </div>

                  <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: "1.5" }}>
                    {wf.description}
                  </p>

                  <div
                    style={{
                      padding: "12px",
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.78rem",
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    <div><strong>Email Subject:</strong> {wf.action_config?.subject}</div>
                    <div style={{ marginTop: "4px", color: "var(--text-muted)" }}>
                      <strong>Template:</strong> "{wf.action_config?.body?.substring(0, 60)}..."
                    </div>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "var(--text-muted)" }}>
                    <span>Executed: <strong>{wf.execution_count}</strong> times</span>
                    <span>Action: Automated Email</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 7: GEMINI AI HUB */}
        {activeTab === "ai_hub" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div
              className="glass-panel"
              style={{
                padding: "24px",
                background: "linear-gradient(135deg, rgba(20, 24, 36, 0.95), rgba(99, 102, 241, 0.2))",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "16px",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <BrainCircuit size={24} color="#818cf8" />
                  <h2 style={{ fontSize: "1.35rem" }}>Google Gemini 3.5 Flash Live Integration</h2>
                </div>
                <p style={{ fontSize: "0.86rem", color: "var(--text-secondary)", maxWidth: "700px" }}>
                  Real-time LLM agent executing dynamic copy generation, churn risk analysis, and webhook NLP triage.
                </p>
              </div>
              <span className="badge badge-vip" style={{ padding: "8px 16px", fontSize: "0.85rem" }}>
                API Key Active & Verified
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "20px" }}>
              <div className="glass-card" style={{ padding: "22px", display: "flex", flexDirection: "column", gap: "14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Sparkles size={18} color="var(--accent-purple)" />
                  <h3 style={{ fontSize: "1rem" }}>Deployment Point 1: Live Gemini Copywriter</h3>
                </div>
                <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                  Synthesizes Indian customer city, RFM spend, and purchase history into tailored high-converting copy.
                </p>

                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  <div>
                    <label style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>Select Customer Profile:</label>
                    <select
                      value={aiSelectedCustomerId}
                      onChange={(e) => setAiSelectedCustomerId(e.target.value)}
                      style={{ width: "100%", marginTop: "4px" }}
                    >
                      {customers.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.first_name} {c.last_name} ({c.billing_address?.city || "India"} - ₹{Number(c.total_spent).toLocaleString('en-IN')})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>Outreach Intent:</label>
                    <select
                      value={aiIntent}
                      onChange={(e) => setAiIntent(e.target.value)}
                      style={{ width: "100%", marginTop: "4px" }}
                    >
                      <option value="festive_loyalty_offer">Diwali / Festive Loyalty Credit</option>
                      <option value="post_purchase_checkin">Post-Purchase Satisfaction Follow-up</option>
                      <option value="churn_reengagement">Cart & Catalog Re-engagement</option>
                    </select>
                  </div>

                  <button
                    onClick={handleRunAIHubDraft}
                    disabled={isAIGenerating}
                    className="btn btn-primary"
                    style={{ marginTop: "4px" }}
                  >
                    <Sparkles size={14} /> {isAIGenerating ? "Calling Gemini..." : "Generate with Live Gemini"}
                  </button>
                </div>

                {aiResult && (
                  <div
                    style={{
                      padding: "12px",
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.8rem",
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                      marginTop: "4px",
                      border: "1px solid rgba(168, 85, 247, 0.3)",
                    }}
                  >
                    <div><strong>Subject:</strong> {aiResult.generated_subject}</div>
                    <div style={{ whiteSpace: "pre-wrap", color: "var(--text-secondary)", fontSize: "0.78rem" }}>
                      {aiResult.generated_body}
                    </div>
                  </div>
                )}
              </div>

              <div className="glass-card" style={{ padding: "22px", display: "flex", flexDirection: "column", gap: "14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Cpu size={18} color="var(--accent-emerald)" />
                  <h3 style={{ fontSize: "1rem" }}>Deployment Point 3: Webhook NLP Triage</h3>
                </div>
                <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                  Intercepts raw unstructured WooCommerce customer notes, extracts urgency, and applies operational tags.
                </p>

                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  <div>
                    <label style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>Incoming Note Text:</label>
                    <textarea
                      rows={3}
                      value={aiTestNote}
                      onChange={(e) => setAiTestNote(e.target.value)}
                      style={{ width: "100%", marginTop: "4px" }}
                    />
                  </div>

                  <button
                    onClick={handleRunAITriage}
                    className="btn btn-secondary"
                  >
                    <Cpu size={14} /> Run NLP Triage Extraction
                  </button>
                </div>

                {aiTriageResult && (
                  <div
                    style={{
                      padding: "12px",
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: "var(--radius-sm)",
                      fontSize: "0.8rem",
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                      border: "1px solid rgba(16, 185, 129, 0.3)",
                    }}
                  >
                    <div>
                      Urgency Level: <span className={`badge badge-${aiTriageResult.inferred_urgency === 'HIGH' ? 'cancelled' : 'completed'}`}>{aiTriageResult.inferred_urgency}</span>
                    </div>
                    <div>
                      Auto-Applied Tags:{" "}
                      {aiTriageResult.auto_applied_tags?.map((t) => (
                        <span key={t} className="badge badge-vip" style={{ marginRight: "4px" }}>{t}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 8: COMMUNICATIONS */}
        {activeTab === "communications" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="glass-panel" style={{ padding: "20px" }}>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "16px" }}>All Dispatched Messages & Workflows</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {communications.map((comm) => (
                  <div
                    key={comm.id}
                    style={{
                      padding: "14px 18px",
                      backgroundColor: "var(--bg-card)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid var(--border-subtle)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span className="badge badge-vip">{comm.channel}</span>
                        <strong style={{ fontSize: "0.9rem" }}>{comm.subject}</strong>
                      </div>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        {new Date(comm.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p style={{ fontSize: "0.84rem", color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                      {comm.content}
                    </p>
                    <div style={{ fontSize: "0.74rem", color: "var(--accent-cyan)", marginTop: "4px" }}>
                      Trigger Source: {comm.trigger_source} • Status: {comm.status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* CUSTOMER 360° DRAWER / MODAL */}
        {selectedCustomer && customerModalData && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundColor: "rgba(0,0,0,0.75)",
              display: "flex",
              justifyContent: "flex-end",
              zIndex: 1000,
              backdropFilter: "blur(6px)",
            }}
          >
            <div
              className="glass-panel"
              style={{
                width: "560px",
                height: "100%",
                borderRadius: "0",
                display: "flex",
                flexDirection: "column",
                overflowY: "auto",
                padding: "28px",
                borderLeft: "1px solid var(--border-subtle)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <div>
                  <h2 style={{ fontSize: "1.3rem" }}>
                    {selectedCustomer.first_name || selectedCustomer.last_name
                      ? `${selectedCustomer.first_name} ${selectedCustomer.last_name}`
                      : selectedCustomer.email}
                  </h2>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
                    <MapPin size={12} /> {selectedCustomer.billing_address?.city || "India"} • Customer 360° Profile
                  </p>
                </div>
                <button
                  onClick={() => setSelectedCustomer(null)}
                  style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                >
                  <X size={22} />
                </button>
              </div>

              {/* Stats Bar */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr 1fr",
                  gap: "10px",
                  padding: "16px",
                  backgroundColor: "var(--bg-surface)",
                  borderRadius: "var(--radius-md)",
                  marginBottom: "20px",
                  textAlign: "center",
                }}
              >
                <div>
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Total LTV</span>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--accent-emerald)" }}>
                    ₹{Number(customerModalData.customer?.total_spent).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Orders Count</span>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                    {customerModalData.customer?.orders_count}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Segment Tier</span>
                  <div style={{ marginTop: "4px" }}>
                    <span className={`badge badge-${customerModalData.customer?.tier.toLowerCase()}`}>
                      {customerModalData.customer?.tier}
                    </span>
                  </div>
                </div>
              </div>

              {/* Contact Info */}
              <div style={{ marginBottom: "24px" }}>
                <h4 style={{ fontSize: "0.95rem", marginBottom: "8px", color: "var(--text-secondary)" }}>Address & Contact</h4>
                <div style={{ fontSize: "0.84rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "4px" }}>
                  <div>Email: <strong style={{ color: "var(--text-primary)" }}>{selectedCustomer.email}</strong></div>
                  <div>Phone: <strong style={{ color: "var(--text-primary)" }}>{selectedCustomer.phone || "+91 Mobile"}</strong></div>
                  <div>
                    Address: <strong style={{ color: "var(--text-primary)" }}>
                      {selectedCustomer.billing_address?.address_1 || "Address"}, {selectedCustomer.billing_address?.city || ""}, {selectedCustomer.billing_address?.postcode || ""}
                    </strong>
                  </div>
                </div>
              </div>

              {/* Quick Communication Box with AI Draft Button */}
              <form onSubmit={handleSendCommunication} style={{ marginBottom: "24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px", flexWrap: "wrap", gap: "8px" }}>
                  <h4 style={{ fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "6px" }}>
                    <Send size={15} color="var(--primary)" />
                    Send Customer Communication
                  </h4>
                  <button
                    type="button"
                    onClick={handleAIDraftInModal}
                    disabled={isAIGenerating}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: "0.76rem", color: "#c084fc", borderColor: "rgba(168, 85, 247, 0.4)" }}
                  >
                    <Sparkles size={12} /> {isAIGenerating ? "Calling Gemini..." : `✨ Context-Aware Draft for ${selectedCustomer.first_name || "Customer"}`}
                  </button>
                </div>

                {/* Autonomous Incentive Safeguard Note */}
                <div style={{ marginBottom: "10px", padding: "8px 12px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                  <span style={{ fontSize: "0.74rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
                    <ShieldCheck size={13} color="#38bdf8" />
                    Gemini autonomously evaluates {selectedCustomer.first_name}'s history to select the best margin-safe incentive.
                  </span>
                  <span style={{ fontSize: "0.7rem", color: "#34d399", fontWeight: 600 }}>
                    Auto Context Mode
                  </span>
                </div>

                <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                  <select
                    value={commChannel}
                    onChange={(e) => setCommChannel(e.target.value)}
                    style={{ flex: 1 }}
                  >
                    <option value="email">Email</option>
                    <option value="sms">SMS / WhatsApp</option>
                    <option value="support_note">Internal Support Note</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Subject..."
                    value={commSubject}
                    onChange={(e) => setCommSubject(e.target.value)}
                    style={{ flex: 2 }}
                  />
                </div>
                <textarea
                  rows={4}
                  placeholder={`Write ${commChannel} message to ${selectedCustomer.first_name || "customer"}...`}
                  value={commContent}
                  onChange={(e) => setCommContent(e.target.value)}
                  style={{ width: "100%", marginBottom: "8px" }}
                />
                <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
                  <Send size={14} /> Dispatch Communication
                </button>
              </form>

              {/* Past Orders */}
              <div style={{ marginBottom: "24px" }}>
                <h4 style={{ fontSize: "0.95rem", marginBottom: "10px" }}>Order History ({customerModalData.orders?.length || 0})</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {customerModalData.orders?.map((ord) => (
                    <div
                      key={ord.id}
                      style={{
                        padding: "10px 12px",
                        backgroundColor: "var(--bg-surface)",
                        borderRadius: "var(--radius-sm)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: "0.82rem",
                      }}
                    >
                      <div>
                        <strong>#{ord.wc_order_id}</strong> • ₹{Number(ord.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                          {ord.line_items?.length} item(s) • {ord.payment_method}
                        </div>
                      </div>
                      <span className={`badge badge-${ord.status}`}>{ord.status}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Communication Timeline */}
              <div>
                <h4 style={{ fontSize: "0.95rem", marginBottom: "10px" }}>Communication History</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {customerModalData.communications?.map((c) => (
                    <div
                      key={c.id}
                      style={{
                        padding: "10px 12px",
                        backgroundColor: "var(--bg-card)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "0.8rem",
                        border: "1px solid var(--border-subtle)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <strong>{c.subject}</strong>
                        <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                          {new Date(c.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                      <div style={{ color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{c.content}</div>
                      <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "4px" }}>
                        Via: {c.trigger_source}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

from typing import Dict, Any, List, Optional
import os
import json
import logging
from datetime import datetime
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Initialize Live Google Gemini Client
_gemini_client = None
if settings.GEMINI_API_KEY:
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info(f"Initialized Google GenAI client with model: {settings.GEMINI_MODEL}")
    except Exception as e:
        logger.warning(f"Could not initialize Google GenAI: {e}")


class AIAgentService:
    INCENTIVE_POLICIES = {
        "free_delivery": {
            "id": "free_delivery",
            "label": "Free Express Delivery",
            "badge": "Zero Product Discount",
            "description": "Waives delivery fee (saves ₹150) using code FREEDELIVERY. 0% discount on product to safeguard profit margins.",
            "code": "FREEDELIVERY",
            "guideline": "Offer free priority express shipping on their next order with promo code FREEDELIVERY. Strictly DO NOT offer any price discount or cash coupons."
        },
        "extended_warranty": {
            "id": "extended_warranty",
            "label": "6-Month Extended Warranty",
            "badge": "Zero Cash Giveaway",
            "description": "Complimentary 6-month CarePlus warranty & accidental coverage. High perceived value without cash outlay.",
            "code": "CAREPLUS",
            "guideline": "Offer a complimentary 6-month extended warranty / CarePlus protection plan on their purchase using code CAREPLUS. Strictly DO NOT offer cash or price discounts."
        },
        "complimentary_gift": {
            "id": "complimentary_gift",
            "label": "Complimentary Tech Gift",
            "badge": "Physical Accessory Sample",
            "description": "Free premium braided charging cable or tech microfiber kit auto-added to their cart with code FREEGIFT.",
            "code": "FREEGIFT",
            "guideline": "Offer a complimentary physical tech accessory gift (premium braided cable or kit) added to their next order with code FREEGIFT. Strictly DO NOT give price cuts."
        },
        "capped_coupon": {
            "id": "capped_coupon",
            "label": "Capped 5% Coupon (Max ₹150)",
            "badge": "Strict Margin Ceiling",
            "description": "Strict 5% coupon capped at ₹150 maximum with code SAVE5. Absolutely prevents heavy discount giveaways.",
            "code": "SAVE5",
            "guideline": "Offer strictly a 5% discount strictly capped at a maximum of ₹150 with promo code SAVE5. Strictly forbid any larger discount or arbitrary vouchers."
        },
        "vip_concierge": {
            "id": "vip_concierge",
            "label": "VIP Concierge (No Discount)",
            "badge": "Zero Financial Cost",
            "description": "White-glove store manager outreach, priority dispatch queue, and early access to product drops. Zero financial giveaway.",
            "code": "None",
            "guideline": "Provide empathetic white-glove check-in from the store manager, priority logistics dispatch, or early access to new drops. Strictly ZERO financial giveaways, ZERO vouchers, and ZERO discounts."
        }
    }

    @classmethod
    def call_gemini(cls, prompt: str) -> Optional[str]:
        """Calls Live Google Gemini API with fallback."""
        if _gemini_client:
            try:
                response = _gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to heuristic synthesis: {e}")
        return None

    # --- 1. Automated Support & Ticket Resolution (Helpdesk) ---

    @classmethod
    def process_helpdesk_ticket(
        cls,
        subject: str,
        message: str,
        customer: Customer,
        orders: List[Order]
    ) -> Dict[str, Any]:
        """
        [Item 1]: Automated Support & Helpdesk Intelligence:
        1. Context-Aware Deflection & Retrieval: Pulls customer orders & city
        2. Sentiment & Urgency Triage: Classifies emotional state & urgency
        3. Ticket Summarization: Generates 2-sentence brief
        4. One-Click Agent Co-pilot: Auto-drafts empathetic resolution reply
        """
        first_name = customer.first_name or customer.email.split("@")[0].capitalize()
        city = customer.billing_address.get("city", "India") if customer.billing_address else "India"
        
        # Order summary context
        order_details = []
        for o in orders:
            items_str = ", ".join(i.get("name", "Product") for i in (o.line_items or []))
            order_details.append(f"Order #{o.wc_order_id} (Status: {o.status}, Items: {items_str}, Total: INR ₹{o.total:,.0f})")
        orders_context = "\n".join(order_details) or "No prior orders"

        prompt = (
            f"You are a Tier-1 Customer Support & Retention AI for KILOWOTT Store India.\n"
            f"Customer Profile:\n"
            f"- Name: {first_name}\n"
            f"- City: {city}, India\n"
            f"- Tier: {customer.tier}\n"
            f"- Orders:\n{orders_context}\n\n"
            f"Inbound Ticket:\n"
            f"Subject: {subject}\n"
            f"Customer Message: \"{message}\"\n\n"
            f"Perform the following four actions and return ONLY a JSON object with these keys:\n"
            f"1. sentiment: (Choose one: 'Frustrated', 'Anxious', 'Neutral', 'Satisfied')\n"
            f"2. urgency: (Choose one: 'High', 'Medium', 'Low')\n"
            f"3. two_sentence_summary: (Exactly 2 sentences summarizing the customer's core complaint and context)\n"
            f"4. agent_copilot_reply: (A complete, empathetic resolution reply referencing their exact order and city. If delayed or frustrated, offer a small INR gesture or concrete delivery status update with warm Indian business etiquette.)\n\n"
            f"Output ONLY raw JSON without markdown formatting."
        )

        llm_response = cls.call_gemini(prompt)
        if llm_response:
            try:
                clean_json = llm_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                return {
                    "sentiment": data.get("sentiment", "Frustrated" if any(w in message.lower() for w in ["delay", "broken", "issue", "urg"]) else "Neutral"),
                    "urgency": data.get("urgency", "High"),
                    "two_sentence_summary": data.get("two_sentence_summary", f"{first_name} in {city} is inquiring regarding their recent order status. The ticket requires immediate operational review."),
                    "agent_copilot_reply": data.get("agent_copilot_reply", f"Namaste {first_name}, thank you for reaching out. We are personally prioritizing your shipment to {city}."),
                    "model": f"Google Gemini ({settings.GEMINI_MODEL}) [Live]"
                }
            except Exception:
                pass

        # Robust Fallback
        is_frustrated = any(w in message.lower() for w in ["delay", "wait", "stuck", "urgent", "wrong", "broken", "where"])
        return {
            "sentiment": "Frustrated" if is_frustrated else "Neutral",
            "urgency": "High" if is_frustrated else "Medium",
            "two_sentence_summary": f"{first_name} from {city} has raised a support inquiry regarding their purchase. The customer requires an expedited status update and proactive resolution.",
            "agent_copilot_reply": f"Namaste {first_name},\n\nWe sincerely apologize for the delay regarding your recent order. Our logistics team in {city} is actively prioritizing your delivery with express transit monitoring.\n\nWarm regards,\nKILOWOTT Customer Care",
            "model": "Heuristic Support Engine"
        }

    # --- 2. Customer Retention & Lifecycle Marketing ---

    @classmethod
    def draft_personalized_communication(
        cls,
        customer: Customer,
        channel: str = "email",
        tone: str = "warm_professional",
        intent: str = "festive_loyalty_offer",
        incentive_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        [Item 3]: Hyper-personalized campaign copy & post-purchase follow-ups.
        Autonomously selects the best margin-safe incentive based on customer context.
        """
        first_name = customer.first_name or customer.email.split("@")[0].capitalize()
        city = customer.billing_address.get("city", "India") if customer.billing_address else "India"
        tier = customer.tier or "Regular"
        ltv = customer.total_spent or 0.0

        prompt = (
            f"You are an Autonomous AI Retention & CRM Agent for KILOWOTT Store India.\n"
            f"Customer Profile:\n"
            f"- Name: {first_name}\n"
            f"- City: {city}, India\n"
            f"- Segment Tier: {tier}\n"
            f"- Lifetime Spend: INR ₹{ltv:,.0f}\n"
            f"- Communication Goal/Intent: {intent}\n"
            f"- Preferred Channel: {channel}\n\n"
            f"MERCHANT GUARDRAIL (STRICT FINANCIAL SAFETY):\n"
            f"Arbitrary large discounts (e.g. ₹500 or 15-20% off) are strictly forbidden to protect merchant profit margins.\n"
            f"Instead, analyze this customer's profile and autonomously choose EXACTLY ONE margin-safe incentive:\n"
            f"- 'free_delivery' (Code: FREEDELIVERY) - Free priority shipping (saves ₹150; 0% product discount).\n"
            f"- 'extended_warranty' (Code: CAREPLUS) - 6-month CarePlus warranty (₹0 cash outlay).\n"
            f"- 'complimentary_gift' (Code: FREEGIFT) - Free physical tech accessory gift auto-added to cart.\n"
            f"- 'capped_coupon' (Code: SAVE5) - Controlled 5% discount capped at max ₹150.\n"
            f"- 'vip_concierge' (Code: None) - White-glove store manager check-in & priority dispatch (₹0 discount).\n\n"
            f"Return your response in JSON format with keys:\n"
            f"1. chosen_incentive: (one of 'free_delivery', 'extended_warranty', 'complimentary_gift', 'capped_coupon', 'vip_concierge')\n"
            f"2. incentive_rationale: (1 sentence explaining why this incentive fits {first_name}'s context)\n"
            f"3. subject: (Catchy subject line)\n"
            f"4. body: (Personalized message with polite Indian business etiquette)\n\n"
            f"Output ONLY raw JSON."
        )

        llm_response = cls.call_gemini(prompt)

        # Context-aware fallback selection
        if tier in ["VIP", "Loyal"] and ltv >= 20000:
            auto_type = "vip_concierge"
            rationale = "Customer is high-LTV VIP who values personalized priority concierge and white-glove recognition without financial discounts."
            fallback_benefit = "Our store manager has personally flagged your profile for white-glove VIP dispatch and dedicated WhatsApp concierge support."
        elif ltv >= 5000:
            auto_type = "extended_warranty"
            rationale = "Customer purchased high-value gear; 6-month CarePlus protection reassures long-term ownership at zero cash cost."
            fallback_benefit = "As a valued customer, we have unlocked a complimentary 6-Month CarePlus Extended Warranty on your gear with code CAREPLUS."
        else:
            auto_type = "free_delivery"
            rationale = "Waiving the ₹150 shipping fee eliminates repeat-purchase friction without discounting product prices."
            fallback_benefit = "Here is an exclusive benefit on your next order: use code FREEDELIVERY for Free Priority Express Shipping across India."

        active_type = auto_type
        chosen_rationale = rationale
        subject = f"Exclusive Benefit for {first_name} from KILOWOTT"
        body = (
            f"Namaste {first_name},\n\n"
            f"Thank you for being part of our {tier} community in {city}! "
            f"With over ₹{ltv:,.0f} in total purchases, we truly appreciate your loyalty.\n\n"
            f"{fallback_benefit}\n\n"
            f"Warm regards,\nKILOWOTT Customer Team"
        )

        if llm_response:
            try:
                clean_text = llm_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                if data.get("chosen_incentive") in cls.INCENTIVE_POLICIES:
                    active_type = data["chosen_incentive"]
                if data.get("incentive_rationale"):
                    chosen_rationale = data["incentive_rationale"]
                if data.get("subject"):
                    subject = data["subject"]
                if data.get("body"):
                    body = data["body"]
            except Exception:
                pass

        policy = cls.INCENTIVE_POLICIES.get(active_type, cls.INCENTIVE_POLICIES["free_delivery"])

        return {
            "channel": channel,
            "tone": tone,
            "intent": intent,
            "incentive_type": active_type,
            "incentive_label": policy["label"],
            "incentive_rationale": chosen_rationale,
            "customer_id": customer.id,
            "customer_name": first_name,
            "generated_subject": subject,
            "generated_body": body,
            "llm_prompt_metadata": {
                "customer_tier": tier,
                "city_context": city,
                "calculated_ltv_inr": f"₹{ltv:,.2f}",
                "model_used": f"Google Gemini ({settings.GEMINI_MODEL}) [Live]" if _gemini_client else "Heuristic Engine"
            }
        }

    @classmethod
    def get_slipping_customers(cls, customers: List[Customer], orders: List[Order]) -> List[Dict[str, Any]]:
        """Dynamic churn intervention detection."""
        slipping_list = []

        for cust in customers:
            cust_orders = [o for o in orders if o.customer_id == cust.id]
            orders_count = len(cust_orders)
            total_spent = cust.total_spent or 0.0
            
            risk_reasons = []
            risk_score = 25

            has_on_hold = any(o.status == "on-hold" for o in cust_orders)
            has_cancelled = any(o.status == "cancelled" for o in cust_orders)

            if orders_count == 0:
                risk_score = 90
                risk_reasons.append("Registered lead with 0 completed purchases")
            elif orders_count == 1:
                risk_score = 70
                risk_reasons.append("Single order placed with no subsequent repeat purchases")
            
            if has_on_hold:
                risk_score = max(risk_score, 85)
                risk_reasons.append("Order currently on-hold awaiting bank/payment resolution")

            if has_cancelled:
                risk_score = max(risk_score, 80)
                risk_reasons.append("History of cancelled orders; potential checkout friction")

            if cust.tier in ["VIP", "Loyal"] and orders_count <= 2:
                risk_score = max(risk_score, 60)
                risk_reasons.append("High potential LTV customer showing cooling purchase cadence")

            if risk_score >= 75:
                risk_level = "HIGH RISK"
            elif risk_score >= 50:
                risk_level = "MODERATE RISK"
            else:
                risk_level = "LOW RISK"

            city = cust.billing_address.get("city", "India") if cust.billing_address else "India"

            slipping_list.append({
                "customer_id": cust.id,
                "name": f"{cust.first_name} {cust.last_name}".strip() or cust.email.split("@")[0].capitalize(),
                "email": cust.email,
                "city": city,
                "tier": cust.tier,
                "orders_count": orders_count,
                "total_spent": total_spent,
                "slip_probability": risk_score,
                "risk_level": risk_level,
                "behavioral_triggers": risk_reasons,
                "recent_order_status": cust_orders[0].status if cust_orders else "none"
            })

        slipping_list.sort(key=lambda x: x["slip_probability"], reverse=True)
        return slipping_list

    @classmethod
    def generate_retention_strategy(
        cls,
        customer: Customer,
        orders: List[Order],
        incentive_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Dynamic Churn Intervention with Gemini:
        Autonomously evaluates the customer's purchase context to select the most appropriate
        margin-safe incentive (Free Delivery, Warranty, Gift, Capped 5%, or VIP Concierge)
        without requiring manual merchant intervention or risking heavy discount giveaways.
        """
        first_name = customer.first_name or customer.email.split("@")[0].capitalize()
        city = customer.billing_address.get("city", "India") if customer.billing_address else "India"
        items_bought = []
        for o in orders:
            for item in (o.line_items or []):
                items_bought.append(item.get("name", "Item"))

        items_str = ", ".join(items_bought[:3]) or "None"
        statuses = [o.status for o in orders] or ["no orders"]

        prompt = (
            f"You are an Autonomous AI Customer Retention Strategist for an Indian e-commerce electronics brand (KILOWOTT).\n"
            f"Customer Profile:\n"
            f"- Name: {first_name}\n"
            f"- Location: {city}, India\n"
            f"- Segment Tier: {customer.tier}\n"
            f"- Lifetime Spend: INR ₹{customer.total_spent:,.0f}\n"
            f"- Total Orders: {len(orders)}\n"
            f"- Past Items Purchased: {items_str}\n"
            f"- Recent Order Statuses: {', '.join(statuses)}\n\n"
            f"MERCHANT GUARDRAIL (STRICT FINANCIAL SAFETY):\n"
            f"Arbitrary large discounts (e.g. ₹500 or 15-20% off) are strictly forbidden to protect merchant profit margins.\n"
            f"Instead, analyze this customer's context and AUTONOMOUSLY SELECT EXACTLY ONE of the 5 authorized margin-safe incentives:\n"
            f"1. 'free_delivery' (Code: FREEDELIVERY) - Free express shipping (saves ₹150; 0% product price discount). Best for shipping friction or single order drop-off.\n"
            f"2. 'extended_warranty' (Code: CAREPLUS) - 6-Month CarePlus warranty on tech purchases (₹0 cash cost). Best for premium electronics/gadgets buyers.\n"
            f"3. 'complimentary_gift' (Code: FREEGIFT) - Free physical tech accessory gift added to cart. Best for repeat accessories/lifestyle shoppers.\n"
            f"4. 'capped_coupon' (Code: SAVE5) - Controlled 5% discount strictly capped at ₹150 max. Best for price-sensitive buyers.\n"
            f"5. 'vip_concierge' (Code: None) - White-glove personal store manager concierge & priority dispatch (₹0 discount). Best for VIP/Loyal high-spend customers.\n\n"
            f"Generate a concrete retention strategy in JSON format with exactly five fields:\n"
            f"1. chosen_incentive_type: (One of: 'free_delivery', 'extended_warranty', 'complimentary_gift', 'capped_coupon', 'vip_concierge')\n"
            f"2. incentive_rationale: (1 concise sentence explaining why this specific incentive fits {first_name}'s context best)\n"
            f"3. behavioral_diagnosis: (1-2 sentences explaining why they are about to slip)\n"
            f"4. retention_action: (1 specific recommended commercial offer applying the chosen incentive)\n"
            f"5. recovery_message: (A ready-to-send recovery message written directly to {first_name} with polite Indian business etiquette applying the chosen incentive)\n\n"
            f"Output ONLY valid JSON without markdown fences."
        )

        llm_response = cls.call_gemini(prompt)

        # Context-aware heuristic selection fallback
        has_tech_items = any(
            any(k in it.lower() for k in ["tv", "keyboard", "headphones", "lamp", "boat", "oneplus", "logitech", "keychron", "laptop", "monitor"])
            for it in items_bought
        )
        if customer.tier in ["VIP", "Loyal"] and customer.total_spent >= 20000:
            auto_type = "vip_concierge"
            auto_rationale = f"{first_name} is a high-LTV VIP customer (₹{customer.total_spent:,.0f}); personalized white-glove outreach builds loyalty without discounting."
        elif has_tech_items:
            auto_type = "extended_warranty"
            auto_rationale = f"{first_name} purchased electronics ({items_str}); a 6-month CarePlus warranty provides high perceived value at ₹0 cost to the merchant."
        elif len(orders) <= 1:
            auto_type = "free_delivery"
            auto_rationale = f"{first_name} placed a single order; Free Express Delivery eliminates shipping friction without discounting product prices."
        else:
            auto_type = "complimentary_gift"
            auto_rationale = f"A complimentary branded accessory gift rewards {first_name}'s repeat patronage without price erosion."

        active_type = incentive_type if (incentive_type and incentive_type != "auto" and incentive_type in cls.INCENTIVE_POLICIES) else auto_type

        # Fallback responses tailored by policy
        fallback_action_map = {
            "free_delivery": f"Dispatch an automated WhatsApp win-back message with code FREEDELIVERY for Free Express Delivery across India (saves ₹150 shipping fee with zero product margin hit).",
            "extended_warranty": f"Activate a complimentary 6-Month CarePlus Extended Warranty on past purchases with code CAREPLUS to restore brand confidence at ₹0 cash cost.",
            "complimentary_gift": f"Send an exclusive re-engagement alert offering a complimentary braided nylon cable added to their next order with code FREEGIFT.",
            "capped_coupon": f"Issue a controlled 5% re-engagement coupon strictly capped at ₹150 with code SAVE5 to protect store margins.",
            "vip_concierge": f"Initiate white-glove customer care outreach from the store manager with priority dispatch queue and dedicated support."
        }

        fallback_msg_map = {
            "free_delivery": f"Namaste {first_name},\n\nWe noticed you haven't visited us recently! As a valued shopper in {city}, we'd love to welcome you back with Free Express Delivery on your next order.\n\nUse code FREEDELIVERY at checkout.\n\nWarm regards,\nKILOWOTT Customer Team",
            "extended_warranty": f"Namaste {first_name},\n\nWe hope your recent purchase is serving you well in {city}. To ensure your complete peace of mind, we're granting you a complimentary 6-Month CarePlus Warranty extension on us.\n\nActivate it with code CAREPLUS on your account.\n\nWarm regards,\nKILOWOTT Customer Team",
            "complimentary_gift": f"Namaste {first_name},\n\nWe'd love to welcome you back to KILOWOTT! On your next order, we are including a complimentary premium tech accessory gift in your package.\n\nSimply enter code FREEGIFT at checkout.\n\nWarm regards,\nKILOWOTT Customer Team",
            "capped_coupon": f"Namaste {first_name},\n\nThank you for being part of our community. As a small token of gratitude, enjoy 5% off (up to ₹150) on your next order with code SAVE5.\n\nWarm regards,\nKILOWOTT Customer Team",
            "vip_concierge": f"Namaste {first_name},\n\nThis is the KILOWOTT Customer Care desk in India. We wanted to personally check in and see how your experience has been. If you ever need expedited assistance or recommendations, our concierge desk is at your direct service.\n\nWarm regards,\nKILOWOTT Management"
        }

        chosen_action = fallback_action_map.get(active_type, fallback_action_map["free_delivery"])
        chosen_msg = fallback_msg_map.get(active_type, fallback_msg_map["free_delivery"])
        chosen_rationale = auto_rationale

        if llm_response:
            try:
                clean_text = llm_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                if data.get("chosen_incentive_type") in cls.INCENTIVE_POLICIES:
                    active_type = data["chosen_incentive_type"]
                policy = cls.INCENTIVE_POLICIES.get(active_type, cls.INCENTIVE_POLICIES["free_delivery"])
                return {
                    "customer_id": customer.id,
                    "customer_name": first_name,
                    "incentive_type": active_type,
                    "incentive_label": policy["label"],
                    "incentive_code": policy["code"],
                    "incentive_rationale": data.get("incentive_rationale", auto_rationale),
                    "behavioral_diagnosis": data.get("behavioral_diagnosis", f"{first_name} has shown a drop in engagement after their purchase in {city}."),
                    "retention_action": data.get("retention_action", chosen_action),
                    "recovery_message": data.get("recovery_message", chosen_msg),
                    "model": f"Google Gemini ({settings.GEMINI_MODEL}) [Live]"
                }
            except Exception:
                pass

        policy = cls.INCENTIVE_POLICIES.get(active_type, cls.INCENTIVE_POLICIES["free_delivery"])
        return {
            "customer_id": customer.id,
            "customer_name": first_name,
            "incentive_type": active_type,
            "incentive_label": policy["label"],
            "incentive_code": policy["code"],
            "incentive_rationale": chosen_rationale,
            "behavioral_diagnosis": f"{first_name} from {city} made {len(orders)} order(s) totaling ₹{customer.total_spent:,.0f}, but has not repeated purchase.",
            "retention_action": chosen_action,
            "recovery_message": chosen_msg,
            "model": "Heuristic Retention Engine"
        }

    @classmethod
    def get_incentive_policies(cls) -> List[Dict[str, Any]]:
        """Returns the list of merchant-selectable incentive policies."""
        return list(cls.INCENTIVE_POLICIES.values())

    # --- 3. Internal CRM Knowledge & Natural Language Database Search ---

    @classmethod
    def natural_language_crm_query(
        cls,
        nl_query: str,
        customers: List[Customer],
        orders: List[Order]
    ) -> Dict[str, Any]:
        """
        [Item 4]: Natural Language Database Search:
        Translates natural language questions like:
        "Which customers in Bengaluru have spent over 20000?" or "Show high risk customers"
        into structured filtering criteria and returns matched rows.
        """
        prompt = (
            f"You are a Natural Language to CRM Query Engine for KILOWOTT E-Commerce India.\n"
            f"The user asks this question: \"{nl_query}\"\n\n"
            f"Extract filtering criteria into a JSON object with these optional keys:\n"
            f"- city: (string or null, e.g. 'Bengaluru', 'Panaji', 'Mumbai', 'Chennai', 'Delhi')\n"
            f"- min_spend: (number or null, e.g. 10000)\n"
            f"- tier: (string or null: 'VIP', 'Loyal', 'New', 'Regular')\n"
            f"- order_status: (string or null: 'pending', 'processing', 'completed', 'on-hold')\n"
            f"- summary_explanation: (1 sentence explaining what was queried)\n\n"
            f"Output ONLY raw JSON."
        )

        llm_response = cls.call_gemini(prompt)
        filters = {}
        explanation = f"Searching for: {nl_query}"

        if llm_response:
            try:
                clean_json = llm_response.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)
                filters = parsed
                explanation = parsed.get("summary_explanation", explanation)
            except Exception:
                pass

        # Apply extracted filters to customers
        city_filter = (filters.get("city") or "").lower()
        min_spend = filters.get("min_spend")
        tier_filter = (filters.get("tier") or "").upper()

        matched_customers = []
        for c in customers:
            c_city = (c.billing_address.get("city", "") if c.billing_address else "").lower()
            if city_filter and city_filter not in c_city:
                continue
            if min_spend and (c.total_spent or 0) < float(min_spend):
                continue
            if tier_filter and c.tier != tier_filter:
                continue
            
            matched_customers.append({
                "id": c.id,
                "name": f"{c.first_name} {c.last_name}".strip(),
                "email": c.email,
                "city": c.billing_address.get("city", "India") if c.billing_address else "India",
                "tier": c.tier,
                "total_spent": c.total_spent,
                "orders_count": c.orders_count
            })

        return {
            "query": nl_query,
            "interpreted_filters": filters,
            "explanation": explanation,
            "matched_count": len(matched_customers),
            "results": matched_customers,
            "model": f"Google Gemini ({settings.GEMINI_MODEL}) [Live]" if _gemini_client else "Heuristic Search"
        }

    @classmethod
    def evaluate_churn_risk_score(cls, customer: Customer, orders: List[Order]) -> Dict[str, Any]:
        ltv = customer.total_spent or 0.0
        orders_count = len(orders)
        
        if ltv >= 30000 and orders_count >= 3:
            risk_level = "LOW"
            score = 14
            rationale = "High LTV repeat customer with consistent UPI checkout velocity across Indian metro hubs."
            recommendation = "Enroll in KILOWOTT Platinum Priority Club; send seasonal exclusive preview invitations."
        elif ltv >= 8000:
            risk_level = "MODERATE"
            score = 42
            rationale = "Healthy transaction history, but over 30 days since last purchase activity."
            recommendation = "Send tailored WhatsApp catalog push with INR ₹500 voucher on accessories."
        else:
            risk_level = "HIGH"
            score = 78
            rationale = "Single-order customer with unverified repeat intent or pending COD orders."
            recommendation = "Automate gentle check-in offering 10% prepaid discount on next cart."

        return {
            "customer_id": customer.id,
            "customer_email": customer.email,
            "churn_risk_score": score,
            "risk_level": risk_level,
            "agent_rationale": rationale,
            "recommended_next_best_action": recommendation
        }

    @classmethod
    def triage_incoming_order_note(cls, customer_note: str) -> Dict[str, Any]:
        note_lower = customer_note.lower()
        tags = []
        urgency = "NORMAL"

        if any(w in note_lower for w in ["urgent", "hurry", "asap", "fast", "wedding", "emergency"]):
            tags.append("EXPEDITE_SHIPPING")
            urgency = "HIGH"
        if any(w in note_lower for w in ["gate", "security", "flat", "door", "call", "desk", "guard"]):
            tags.append("SPECIAL_DELIVERY_INSTRUCTION")
        if any(w in note_lower for w in ["bill", "gst", "invoice", "company", "tax"]):
            tags.append("GST_INVOICE_REQUIRED")

        return {
            "original_note": customer_note,
            "inferred_urgency": urgency,
            "auto_applied_tags": tags,
            "action_required": urgency == "HIGH"
        }

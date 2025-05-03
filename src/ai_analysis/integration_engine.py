# -*- coding: utf-8 -*-
"""
Integration Engine Module

This module combines insights from all analyzers using reinforcement learning algorithms
to create a comprehensive understanding of the user's current state and future trajectory.
It considers the complex interactions between health, lifestyle, financial, and social factors.
"""

import logging
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class IntegrationEngine:
    """
    Integrates insights from all analyzers and creates comprehensive recommendations
    
    This engine uses reinforcement learning to understand the complex relationships
    between different aspects of life and aging, then generates personalized
    recommendations that consider trade-offs and interactions between factors.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model_type = "ReinforcementLearningIntegration"
        logger.info("Integration Engine initialized")
    
    def integrate_insights(self, 
                          user_id: str,
                          health_insights: Optional[Dict[str, Any]] = None,
                          aging_insights: Optional[Dict[str, Any]] = None,
                          disease_insights: Optional[Dict[str, Any]] = None,
                          lifestyle_insights: Optional[Dict[str, Any]] = None,
                          financial_insights: Optional[Dict[str, Any]] = None,
                          social_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Integrate insights from all analysis modules
        
        Args:
            user_id: User identifier
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            Dict containing integrated insights and recommendations
        """
        logger.info(f"Integrating insights for user {user_id}")
        
        # Prepare input data
        input_data = self._prepare_input_data(
            health_insights, aging_insights, disease_insights,
            lifestyle_insights, financial_insights, social_insights
        )
        
        try:
            # Use the latest integration model
            results = self.model_manager.predict_with_latest(self.model_type, input_data)
            
            # Enhance results with additional information
            enhanced_results = self._enhance_results(
                results, health_insights, aging_insights, disease_insights,
                lifestyle_insights, financial_insights, social_insights
            )
            
            logger.info(f"Completed insight integration for user {user_id}")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error integrating insights: {e}")
            # Return basic results in case of error
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def _prepare_input_data(self, 
                           health_insights: Optional[Dict[str, Any]] = None,
                           aging_insights: Optional[Dict[str, Any]] = None,
                           disease_insights: Optional[Dict[str, Any]] = None,
                           lifestyle_insights: Optional[Dict[str, Any]] = None,
                           financial_insights: Optional[Dict[str, Any]] = None,
                           social_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare and normalize input data for the integration model
        
        Args:
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            Normalized and prepared input data
        """
        input_data = {
            "timestamp": time.time(),
            "health": {},
            "aging": {},
            "disease": {},
            "lifestyle": {},
            "financial": {},
            "social": {}
        }
        
        # Extract key metrics from health insights
        if health_insights:
            input_data["health"]["status"] = health_insights.get("health_status", "unknown")
            input_data["health"]["score"] = health_insights.get("health_score", 0)
            
            # Extract key health parameters
            params = health_insights.get("parameter_analysis", {})
            for param, analysis in params.items():
                input_data["health"][param] = analysis.get("status", "unknown")
            
            # Extract risk factors
            input_data["health"]["risk_factors"] = health_insights.get("risk_factors", [])
        
        # Extract key metrics from aging insights
        if aging_insights:
            input_data["aging"]["biological_age"] = aging_insights.get("biological_age", 0)
            input_data["aging"]["chronological_age"] = aging_insights.get("chronological_age", 0)
            input_data["aging"]["aging_rate"] = aging_insights.get("aging_rate", 1.0)
            
            if "biological_age" in aging_insights and "chronological_age" in aging_insights:
                input_data["aging"]["age_difference"] = aging_insights["biological_age"] - aging_insights["chronological_age"]
            
            # Extract contributing factors
            factors = aging_insights.get("contributing_factors", [])
            positive_factors = [f["factor"] for f in factors if f.get("impact") == "positive"]
            negative_factors = [f["factor"] for f in factors if f.get("impact") == "negative"]
            
            input_data["aging"]["positive_factors"] = positive_factors
            input_data["aging"]["negative_factors"] = negative_factors
        
        # Extract key metrics from disease insights
        if disease_insights:
            input_data["disease"]["overall_risk"] = disease_insights.get("overall_risk", 0)
            
            # Extract specific disease risks
            risks = disease_insights.get("disease_risks", {})
            for disease, risk in risks.items():
                input_data["disease"][f"{disease}_risk"] = risk
            
            # Extract preventable risks
            input_data["disease"]["preventable_risks"] = disease_insights.get("preventable_risks", [])
        
        # Extract key metrics from lifestyle insights
        if lifestyle_insights:
            input_data["lifestyle"]["overall_score"] = lifestyle_insights.get("overall_score", 0)
            
            # Extract specific lifestyle factors
            for factor in ["physical_activity", "sleep", "diet", "stress", "smoking", "alcohol"]:
                if factor in lifestyle_insights:
                    input_data["lifestyle"][factor] = lifestyle_insights[factor]
            
            # Extract lifestyle improvement potential
            input_data["lifestyle"]["improvement_potential"] = lifestyle_insights.get("improvement_potential", 0)
        
        # Extract key metrics from financial insights
        if financial_insights:
            input_data["financial"]["health_score"] = financial_insights.get("financial_health_score", 0)
            input_data["financial"]["savings_adequacy"] = financial_insights.get("savings_adequacy", 0)
            input_data["financial"]["retirement_readiness"] = financial_insights.get("retirement_readiness", 0)
            
            # Extract financial concerns
            input_data["financial"]["concerns"] = financial_insights.get("concerns", [])
            
            # Extract healthcare cost preparedness
            input_data["financial"]["healthcare_preparedness"] = financial_insights.get("healthcare_preparedness", 0)
        
        # Extract key metrics from social insights
        if social_insights:
            input_data["social"]["network_strength"] = social_insights.get("network_strength", 0)
            input_data["social"]["support_level"] = social_insights.get("support_level", 0)
            input_data["social"]["connection_quality"] = social_insights.get("connection_quality", 0)
            
            # Extract social connection types
            input_data["social"]["connection_types"] = social_insights.get("connection_types", [])
            
            # Extract social activity level
            input_data["social"]["activity_level"] = social_insights.get("activity_level", 0)
        
        return input_data
    
    def _enhance_results(self, 
                        model_results: Dict[str, Any],
                        health_insights: Optional[Dict[str, Any]] = None,
                        aging_insights: Optional[Dict[str, Any]] = None,
                        disease_insights: Optional[Dict[str, Any]] = None,
                        lifestyle_insights: Optional[Dict[str, Any]] = None,
                        financial_insights: Optional[Dict[str, Any]] = None,
                        social_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance model results with additional insights and explanations
        
        Args:
            model_results: Raw model prediction results
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            Enhanced results with additional context and explanations
        """
        enhanced = model_results.copy()
        
        # Add timestamp if not present
        if "prediction_time" not in enhanced:
            enhanced["prediction_time"] = time.time()
        
        # Add overall assessment
        enhanced["overall_assessment"] = self._generate_overall_assessment(
            health_insights, aging_insights, disease_insights,
            lifestyle_insights, financial_insights, social_insights
        )
        
        # Enhance recommendations with explanations and cross-domain impacts
        if "recommended_actions" in enhanced:
            enhanced_recommendations = []
            
            for rec in enhanced["recommended_actions"]:
                enhanced_rec = rec.copy()
                
                # Add detailed explanation
                enhanced_rec["detailed_explanation"] = self._generate_recommendation_explanation(
                    rec["action"], health_insights, aging_insights, disease_insights,
                    lifestyle_insights, financial_insights, social_insights
                )
                
                # Add cross-domain impacts
                enhanced_rec["cross_domain_impacts"] = self._generate_cross_domain_impacts(
                    rec["action"], health_insights, aging_insights, disease_insights,
                    lifestyle_insights, financial_insights, social_insights
                )
                
                enhanced_recommendations.append(enhanced_rec)
            
            enhanced["recommended_actions"] = enhanced_recommendations
        
        # Add projected outcomes with timeline
        if "expected_outcomes" in enhanced:
            timeline_outcomes = {}
            
            for outcome, value in enhanced["expected_outcomes"].items():
                timeline_outcomes[outcome] = {
                    "short_term": value * 0.2,  # 20% of total improvement in short term
                    "medium_term": value * 0.5,  # 50% of total improvement in medium term
                    "long_term": value,         # 100% of total improvement in long term
                    "description": self._generate_outcome_description(outcome, value)
                }
            
            enhanced["timeline_outcomes"] = timeline_outcomes
        
        # Add holistic life balance assessment
        enhanced["life_balance"] = self._generate_life_balance_assessment(
            health_insights, aging_insights, disease_insights,
            lifestyle_insights, financial_insights, social_insights
        )
        
        # Add implementation plan with steps
        if "recommended_actions" in enhanced:
            enhanced["implementation_plan"] = self._generate_implementation_plan(
                enhanced["recommended_actions"]
            )
        
        return enhanced
    
    def _generate_overall_assessment(self,
                                   health_insights: Optional[Dict[str, Any]] = None,
                                   aging_insights: Optional[Dict[str, Any]] = None,
                                   disease_insights: Optional[Dict[str, Any]] = None,
                                   lifestyle_insights: Optional[Dict[str, Any]] = None,
                                   financial_insights: Optional[Dict[str, Any]] = None,
                                   social_insights: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an overall assessment considering all domains
        
        Args:
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            String containing overall assessment
        """
        # Collect scores from different domains
        scores = {}
        
        if health_insights and "health_score" in health_insights:
            scores["health"] = health_insights["health_score"]
        
        if aging_insights and "aging_rate" in aging_insights:
            # Convert aging rate to a score (lower rate is better)
            scores["aging"] = max(0, min(100, 100 * (2 - aging_insights["aging_rate"])))
        
        if disease_insights and "overall_risk" in disease_insights:
            # Convert risk to a score (lower risk is better)
            scores["disease"] = max(0, min(100, 100 * (1 - disease_insights["overall_risk"])))
        
        if lifestyle_insights and "overall_score" in lifestyle_insights:
            scores["lifestyle"] = lifestyle_insights["overall_score"]
        
        if financial_insights and "financial_health_score" in financial_insights:
            scores["financial"] = financial_insights["financial_health_score"]
        
        if social_insights and "network_strength" in social_insights:
            scores["social"] = social_insights["network_strength"]
        
        # Calculate overall score if we have enough domain scores
        if len(scores) >= 3:
            overall_score = sum(scores.values()) / len(scores)
            
            # Generate assessment based on overall score
            if overall_score >= 85:
                assessment = "Your overall well-being is excellent across multiple dimensions of health, aging, and life quality. Your current lifestyle and practices are supporting healthy aging and long-term wellness. Continue with your current approach while making minor optimizations as suggested in the recommendations."
            elif overall_score >= 70:
                assessment = "Your overall well-being is good, with strengths in several areas. There are some opportunities for improvement that could significantly enhance your long-term health and aging trajectory. Focus on the high-priority recommendations to address specific areas for improvement."
            elif overall_score >= 50:
                assessment = "Your overall well-being is moderate, with a mix of strengths and areas needing attention. The recommendations provided address key opportunities to improve your health trajectory and aging process. Consider implementing these changes systematically for best results."
            else:
                assessment = "Your overall assessment indicates several areas that need attention to improve your health trajectory and aging process. The recommendations provided focus on the most impactful changes you can make to enhance your well-being. Consider consulting with healthcare professionals for personalized guidance."
            
            # Add domain-specific insights
            domain_insights = []
            
            for domain, score in scores.items():
                if score >= 85:
                    domain_insights.append(f"Your {domain} indicators are excellent.")
                elif score >= 70:
                    domain_insights.append(f"Your {domain} indicators are good.")
                elif score >= 50:
                    domain_insights.append(f"Your {domain} indicators are moderate and could benefit from attention.")
                else:
                    domain_insights.append(f"Your {domain} indicators need significant attention.")
            
            if domain_insights:
                assessment += " " + " ".join(domain_insights)
            
            return assessment
        else:
            # Not enough information for a complete assessment
            return "Based on the available information, a partial assessment has been generated. For a more comprehensive evaluation, additional data from health, aging, lifestyle, financial, and social domains would be beneficial."
    
    def _generate_recommendation_explanation(self,
                                          action: str,
                                          health_insights: Optional[Dict[str, Any]] = None,
                                          aging_insights: Optional[Dict[str, Any]] = None,
                                          disease_insights: Optional[Dict[str, Any]] = None,
                                          lifestyle_insights: Optional[Dict[str, Any]] = None,
                                          financial_insights: Optional[Dict[str, Any]] = None,
                                          social_insights: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate detailed explanation for a recommendation
        
        Args:
            action: The recommended action
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            String containing detailed explanation
        """
        # Generate explanation based on the type of action
        action_lower = action.lower()
        
        if "physical activity" in action_lower or "exercise" in action_lower:
            explanation = "Regular physical activity is one of the most powerful interventions for healthy aging. "
            
            if aging_insights and "contributing_factors" in aging_insights:
                factors = aging_insights["contributing_factors"]
                for factor in factors:
                    if factor["factor"] == "Physical activity" and factor["impact"] == "negative":
                        explanation += factor["description"] + " "
            
            if disease_insights and "disease_risks" in disease_insights:
                risks = disease_insights["disease_risks"]
                relevant_diseases = []
                
                if "cardiovascular_disease" in risks and risks["cardiovascular_disease"] > 0.1:
                    relevant_diseases.append("cardiovascular disease")
                if "diabetes_type_2" in risks and risks["diabetes_type_2"] > 0.1:
                    relevant_diseases.append("type 2 diabetes")
                if "alzheimers" in risks and risks["alzheimers"] > 0.1:
                    relevant_diseases.append("Alzheimer's disease")
                
                if relevant_diseases:
                    diseases_str = ", ".join(relevant_diseases)
                    explanation += f"Increasing physical activity can significantly reduce your risk of {diseases_str}. "
            
            explanation += "Aim for at least 150 minutes of moderate-intensity or 75 minutes of vigorous-intensity aerobic activity per week, plus muscle-strengthening activities at least twice a week."
            
            return explanation
        
        elif "sleep" in action_lower:
            explanation = "Quality sleep is essential for cellular repair, cognitive function, and metabolic health. "
            
            if aging_insights and "contributing_factors" in aging_insights:
                factors = aging_insights["contributing_factors"]
                for factor in factors:
                    if factor["factor"] == "Sleep" and factor["impact"] == "negative":
                        explanation += factor["description"] + " "
            
            if health_insights and "risk_factors" in health_insights:
                if "irregular_sleep" in health_insights["risk_factors"]:
                    explanation += "Your irregular sleep patterns may be affecting your health restoration processes. "
            
            explanation += "Aim for 7-8 hours of quality sleep per night, maintaining a consistent sleep schedule. Consider creating a relaxing bedtime routine and optimizing your sleep environment by reducing light and noise."
            
            return explanation
        
        elif "diet" in action_lower or "nutrition" in action_lower:
            explanation = "Your diet significantly impacts cellular function, inflammation levels, and disease risk. "
            
            if aging_insights and "contributing_factors" in aging_insights:
                factors = aging_insights["contributing_factors"]
                for factor in factors:
                    if factor["factor"] == "Diet" and factor["impact"] == "negative":
                        explanation += factor["description"] + " "
            
            if disease_insights and "disease_risks" in disease_insights:
                risks = disease_insights["disease_risks"]
                diet_related_risks = []
                
                if "cardiovascular_disease" in risks and risks["cardiovascular_disease"] > 0.1:
                    diet_related_risks.append("cardiovascular disease")
                if "diabetes_type_2" in risks and risks["diabetes_type_2"] > 0.1:
                    diet_related_risks.append("type 2 diabetes")
                
                if diet_related_risks:
                    risks_str = ", ".join(diet_related_risks)
                    explanation += f"Improving your diet can help reduce your risk of {risks_str}. "
            
            explanation += "Focus on a balanced diet rich in vegetables, fruits, whole grains, lean proteins, and healthy fats. Minimize processed foods, added sugars, and excessive salt. Consider the Mediterranean or DASH diet patterns, which are associated with longevity and reduced disease risk."
            
            return explanation
        
        elif "stress" in action_lower:
            explanation = "Chronic stress accelerates biological aging through inflammatory and hormonal pathways. "
            
            if aging_insights and "contributing_factors" in aging_insights:
                factors = aging_insights["contributing_factors"]
                for factor in factors:
                    if factor["factor"] == "Stress" and factor["impact"] == "negative":
                        explanation += factor["description"] + " "
            
            if health_insights and "risk_factors" in health_insights:
                if "high_stress" in health_insights["risk_factors"]:
                    explanation += "Your high stress levels may be affecting multiple body systems. "
            
            explanation += "Implement stress management techniques such as meditation, deep breathing exercises, progressive muscle relaxation, or mindfulness practice. Aim for at least 10-15 minutes daily. Consider reducing sources of stress when possible and improving your work-life balance."
            
            return explanation
        
        elif "financial" in action_lower or "retirement" in action_lower:
            explanation = "Financial security is a key component of successful aging, reducing stress and enabling access to healthcare and support services. "
            
            if financial_insights and "concerns" in financial_insights:
                concerns = financial_insights["concerns"]
                if concerns:
                    concerns_str = ", ".join(concerns[:2])  # List first two concerns
                    explanation += f"Addressing financial concerns related to {concerns_str} can reduce stress and improve long-term security. "
            
            if financial_insights and "retirement_readiness" in financial_insights:
                readiness = financial_insights["retirement_readiness"]
                if readiness < 0.5:
                    explanation += "Improving your retirement readiness will help ensure you have adequate resources for healthcare and lifestyle needs as you age. "
            
            explanation += "Consider consulting with a financial advisor to develop a comprehensive plan addressing retirement savings, healthcare costs, and long-term care needs. Review and adjust your savings rate, investment allocation, and insurance coverage as needed."
            
            return explanation
        
        elif "social" in action_lower or "connection" in action_lower:
            explanation = "Strong social connections are strongly linked to longevity, cognitive health, and overall well-being. "
            
            if social_insights and "connection_quality" in social_insights:
                quality = social_insights["connection_quality"]
                if quality < 0.5:
                    explanation += "Improving the quality of your social connections could have significant benefits for your emotional and physical health. "
            
            if social_insights and "connection_types" in social_insights:
                types = social_insights["connection_types"]
                missing_types = []
                
                if "family" not in types:
                    missing_types.append("family")
                if "friends" not in types:
                    missing_types.append("friends")
                if "community" not in types:
                    missing_types.append("community")
                
                if missing_types:
                    missing_str = ", ".join(missing_types)
                    explanation += f"Consider diversifying your social network to include more {missing_str} connections. "
            
            explanation += "Actively nurture existing relationships and seek new social connections through community activities, volunteering, or groups based on shared interests. Aim for regular meaningful interactions and cultivate a diverse social network that provides different types of support."
            
            return explanation
        
        # General explanation for other actions
        return f"This recommendation is based on the integrated analysis of your health, aging, lifestyle, and other factors. Implementing this change could significantly improve your overall well-being and aging trajectory."
    
    def _generate_cross_domain_impacts(self,
                                    action: str,
                                    health_insights: Optional[Dict[str, Any]] = None,
                                    aging_insights: Optional[Dict[str, Any]] = None,
                                    disease_insights: Optional[Dict[str, Any]] = None,
                                    lifestyle_insights: Optional[Dict[str, Any]] = None,
                                    financial_insights: Optional[Dict[str, Any]] = None,
                                    social_insights: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        Generate cross-domain impacts for a recommendation
        
        Args:
            action: The recommended action
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            List of dictionaries containing domain and impact description
        """
        impacts = []
        action_lower = action.lower()
        
        # Physical activity impacts
        if "physical activity" in action_lower or "exercise" in action_lower:
            impacts.append({
                "domain": "Health",
                "impact": "Improves cardiovascular health, strengthens muscles and bones, enhances immune function"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Reduces biological age by improving telomere maintenance and mitochondrial function"
            })
            impacts.append({
                "domain": "Disease Risk",
                "impact": "Reduces risk of cardiovascular disease, diabetes, and certain cancers"
            })
            impacts.append({
                "domain": "Cognitive",
                "impact": "Enhances brain function and may reduce risk of cognitive decline"
            })
            impacts.append({
                "domain": "Financial",
                "impact": "May reduce long-term healthcare costs through disease prevention"
            })
        
        # Sleep impacts
        elif "sleep" in action_lower:
            impacts.append({
                "domain": "Health",
                "impact": "Supports immune function, hormonal balance, and cellular repair"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Optimizes cellular regeneration and reduces inflammation"
            })
            impacts.append({
                "domain": "Cognitive",
                "impact": "Enhances memory consolidation and cognitive performance"
            })
            impacts.append({
                "domain": "Emotional",
                "impact": "Improves mood regulation and stress management"
            })
            impacts.append({
                "domain": "Productivity",
                "impact": "Increases daytime alertness and work efficiency"
            })
        
        # Diet impacts
        elif "diet" in action_lower or "nutrition" in action_lower:
            impacts.append({
                "domain": "Health",
                "impact": "Provides essential nutrients for optimal body function"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Reduces oxidative stress and supports cellular function"
            })
            impacts.append({
                "domain": "Disease Risk",
                "impact": "Lowers risk of metabolic disorders and inflammatory conditions"
            })
            impacts.append({
                "domain": "Energy",
                "impact": "Stabilizes energy levels throughout the day"
            })
            impacts.append({
                "domain": "Financial",
                "impact": "May reduce long-term healthcare costs through better health maintenance"
            })
        
        # Stress management impacts
        elif "stress" in action_lower:
            impacts.append({
                "domain": "Health",
                "impact": "Reduces inflammatory responses and normalizes hormonal balance"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Decreases cellular damage from chronic stress hormones"
            })
            impacts.append({
                "domain": "Cognitive",
                "impact": "Improves focus, decision-making, and cognitive resilience"
            })
            impacts.append({
                "domain": "Social",
                "impact": "Enhances relationship quality through better emotional regulation"
            })
            impacts.append({
                "domain": "Sleep",
                "impact": "Improves sleep quality and reduces insomnia"
            })
        
        # Financial planning impacts
        elif "financial" in action_lower or "retirement" in action_lower:
            impacts.append({
                "domain": "Psychological",
                "impact": "Reduces anxiety and stress about future security"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Ensures access to quality healthcare and support services in later life"
            })
            impacts.append({
                "domain": "Lifestyle",
                "impact": "Enables maintaining desired quality of life throughout aging"
            })
            impacts.append({
                "domain": "Independence",
                "impact": "Supports autonomy and choice in living arrangements and care"
            })
            impacts.append({
                "domain": "Legacy",
                "impact": "Facilitates wealth transfer and charitable giving if desired"
            })
        
        # Social connection impacts
        elif "social" in action_lower or "connection" in action_lower:
            impacts.append({
                "domain": "Health",
                "impact": "Strengthens immune function and reduces inflammation"
            })
            impacts.append({
                "domain": "Aging",
                "impact": "Associated with longer lifespan and reduced mortality risk"
            })
            impacts.append({
                "domain": "Cognitive",
                "impact": "Maintains cognitive function and reduces dementia risk"
            })
            impacts.append({
                "domain": "Emotional",
                "impact": "Provides emotional support and reduces depression risk"
            })
            impacts.append({
                "domain": "Practical",
                "impact": "Creates support network for practical assistance when needed"
            })
        
        # If no specific impacts identified, add general impacts
        if not impacts:
            impacts = [
                {
                    "domain": "Overall Health",
                    "impact": "Likely to improve general health markers and functional capacity"
                },
                {
                    "domain": "Aging Process",
                    "impact": "May contribute to healthier aging and improved quality of life"
                },
                {
                    "domain": "Long-term Wellbeing",
                    "impact": "Could enhance overall life satisfaction and functioning"
                }
            ]
        
        return impacts
    
    def _generate_outcome_description(self, outcome: str, value: float) -> str:
        """
        Generate description for an expected outcome
        
        Args:
            outcome: The name of the outcome
            value: The expected improvement value
            
        Returns:
            String describing the outcome and its significance
        """
        if outcome == "health_improvement":
            if value >= 0.2:
                return f"Substantial health improvements expected, potentially including better biomarkers, increased energy levels, and enhanced physical function."
            elif value >= 0.1:
                return f"Moderate health improvements expected, likely to be noticeable in daily function and energy levels."
            else:
                return f"Modest health improvements expected, which may be subtle but contribute to long-term wellbeing."
        
        elif outcome == "longevity_increase":
            # Value is in years
            if value >= 3:
                return f"Significant potential increase in lifespan of approximately {value:.1f} years, based on improvements to key mortality risk factors."
            elif value >= 1:
                return f"Moderate potential increase in lifespan of approximately {value:.1f} years, reflecting improvements to several health parameters."
            else:
                return f"Modest potential increase in lifespan of approximately {value:.1f} years, representing incremental improvements to health factors."
        
        elif outcome == "financial_security":
            if value >= 0.3:
                return f"Substantial improvement in financial security expected, potentially providing significant peace of mind and options for the future."
            elif value >= 0.15:
                return f"Moderate improvement in financial security expected, strengthening your position for future needs and contingencies."
            else:
                return f"Modest improvement in financial security expected, representing progress toward long-term stability."
        
        elif outcome == "disease_risk_reduction":
            if value >= 0.3:
                return f"Significant reduction in disease risk expected, potentially decreasing the likelihood of developing chronic conditions by up to 30%."
            elif value >= 0.15:
                return f"Moderate reduction in disease risk expected, with notable decreases in the likelihood of several common conditions."
            else:
                return f"Some reduction in disease risk expected, which may have cumulative benefits over time."
        
        elif outcome == "cognitive_function":
            if value >= 0.25:
                return f"Substantial improvements in cognitive function possible, including better memory, focus, and mental clarity."
            elif value >= 0.1:
                return f"Moderate improvements in cognitive performance expected, supporting daily mental tasks and long-term brain health."
            else:
                return f"Some enhancement of cognitive function expected, contributing to mental resilience."
        
        # Generic description for other outcomes
        if value >= 0.25:
            return f"Substantial improvement expected in this area, representing significant positive change."
        elif value >= 0.1:
            return f"Moderate improvement expected in this area, representing meaningful positive change."
        else:
            return f"Some improvement expected in this area, representing incremental positive change."
    
    def _generate_life_balance_assessment(self,
                                        health_insights: Optional[Dict[str, Any]] = None,
                                        aging_insights: Optional[Dict[str, Any]] = None,
                                        disease_insights: Optional[Dict[str, Any]] = None,
                                        lifestyle_insights: Optional[Dict[str, Any]] = None,
                                        financial_insights: Optional[Dict[str, Any]] = None,
                                        social_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a holistic life balance assessment
        
        Args:
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            Dictionary containing life balance assessment
        """
        # Define domains and their weights in overall balance
        domains = {
            "physical": {"weight": 0.2, "score": 0, "description": ""},
            "mental": {"weight": 0.2, "score": 0, "description": ""},
            "social": {"weight": 0.2, "score": 0, "description": ""},
            "financial": {"weight": 0.2, "score": 0, "description": ""},
            "purpose": {"weight": 0.2, "score": 0, "description": ""}
        }
        
        # Assess physical domain
        if health_insights and "health_score" in health_insights:
            domains["physical"]["score"] = health_insights["health_score"] / 100
        elif aging_insights and "aging_rate" in aging_insights:
            # Convert aging rate to a score (lower rate is better)
            domains["physical"]["score"] = max(0, min(1, (2 - aging_insights["aging_rate"]) / 2))
        
        if domains["physical"]["score"] >= 0.8:
            domains["physical"]["description"] = "Your physical well-being is excellent, supporting healthy aging and vitality."
        elif domains["physical"]["score"] >= 0.6:
            domains["physical"]["description"] = "Your physical well-being is good, with some areas that could be enhanced."
        elif domains["physical"]["score"] >= 0.4:
            domains["physical"]["description"] = "Your physical well-being is moderate, with several opportunities for improvement."
        else:
            domains["physical"]["description"] = "Your physical well-being needs attention in multiple areas."
        
        # Assess mental domain
        mental_indicators = []
        if health_insights and "stress_level" in health_insights:
            # Convert stress level to a score (lower stress is better)
            stress_score = max(0, min(1, (10 - health_insights["stress_level"]) / 10))
            mental_indicators.append(stress_score)
        
        if lifestyle_insights and "stress" in lifestyle_insights:
            # Convert stress level to a score (lower stress is better)
            stress_score = max(0, min(1, (10 - lifestyle_insights["stress"]) / 10))
            mental_indicators.append(stress_score)
        
        if lifestyle_insights and "sleep" in lifestyle_insights:
            sleep = lifestyle_insights["sleep"]
            if isinstance(sleep, dict) and "quality_score" in sleep:
                mental_indicators.append(sleep["quality_score"])
        
        if mental_indicators:
            domains["mental"]["score"] = sum(mental_indicators) / len(mental_indicators)
        
        if domains["mental"]["score"] >= 0.8:
            domains["mental"]["description"] = "Your mental well-being is excellent, with effective stress management and cognitive function."
        elif domains["mental"]["score"] >= 0.6:
            domains["mental"]["description"] = "Your mental well-being is good, with some opportunities to enhance stress management or cognitive health."
        elif domains["mental"]["score"] >= 0.4:
            domains["mental"]["description"] = "Your mental well-being is moderate, with several areas that could benefit from attention."
        else:
            domains["mental"]["description"] = "Your mental well-being needs significant attention to improve stress management and cognitive health."
        
        # Assess social domain
        if social_insights:
            social_scores = []
            if "network_strength" in social_insights:
                social_scores.append(social_insights["network_strength"] / 100)
            if "support_level" in social_insights:
                social_scores.append(social_insights["support_level"] / 100)
            if "connection_quality" in social_insights:
                social_scores.append(social_insights["connection_quality"] / 100)
            
            if social_scores:
                domains["social"]["score"] = sum(social_scores) / len(social_scores)
        
        if domains["social"]["score"] >= 0.8:
            domains["social"]["description"] = "Your social connections are strong, providing excellent support and enrichment."
        elif domains["social"]["score"] >= 0.6:
            domains["social"]["description"] = "Your social connections are good, with some opportunities to enhance your support network."
        elif domains["social"]["score"] >= 0.4:
            domains["social"]["description"] = "Your social connections are moderate, with several areas that could be strengthened."
        else:
            domains["social"]["description"] = "Your social connections need attention to build a stronger support network."
        
        # Assess financial domain
        if financial_insights:
            financial_scores = []
            if "financial_health_score" in financial_insights:
                financial_scores.append(financial_insights["financial_health_score"] / 100)
            if "savings_adequacy" in financial_insights:
                financial_scores.append(financial_insights["savings_adequacy"])
            if "retirement_readiness" in financial_insights:
                financial_scores.append(financial_insights["retirement_readiness"])
            
            if financial_scores:
                domains["financial"]["score"] = sum(financial_scores) / len(financial_scores)
        
        if domains["financial"]["score"] >= 0.8:
            domains["financial"]["description"] = "Your financial well-being is excellent, providing strong security for current and future needs."
        elif domains["financial"]["score"] >= 0.6:
            domains["financial"]["description"] = "Your financial well-being is good, with some areas to enhance for long-term security."
        elif domains["financial"]["score"] >= 0.4:
            domains["financial"]["description"] = "Your financial well-being is moderate, with several areas that need attention."
        else:
            domains["financial"]["description"] = "Your financial well-being needs significant attention to build long-term security."
        
        # Assess purpose domain (this is often more qualitative and may not have direct metrics)
        # For now, we'll use a placeholder or derive from other domains
        purpose_indicators = []
        if lifestyle_insights and "satisfaction" in lifestyle_insights:
            purpose_indicators.append(lifestyle_insights["satisfaction"] / 100)
        
        # In absence of direct metrics, we'll use a moderate default score
        if not purpose_indicators:
            domains["purpose"]["score"] = 0.6
        else:
            domains["purpose"]["score"] = sum(purpose_indicators) / len(purpose_indicators)
        
        domains["purpose"]["description"] = "Purpose and meaning are important dimensions of well-being that come from engaging in meaningful activities, contributing to others, and having a sense of direction. Consider reflecting on your values and how your activities align with them."
        
        # Calculate overall balance score
        balance_score = sum(domain["weight"] * domain["score"] for domain in domains.values())
        
        # Generate overall balance description
        if balance_score >= 0.8:
            balance_description = "Your life shows excellent balance across multiple dimensions, supporting optimal aging and well-being."
        elif balance_score >= 0.6:
            balance_description = "Your life shows good balance overall, with some areas that could be strengthened for optimal aging."
        elif balance_score >= 0.4:
            balance_description = "Your life shows moderate balance, with several dimensions that need attention for better aging outcomes."
        else:
            balance_description = "Your life balance needs significant attention across multiple dimensions to support healthy aging."
        
        return {
            "domains": domains,
            "overall_score": balance_score,
            "description": balance_description
        }
    
    def _generate_implementation_plan(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an implementation plan for the recommendations
        
        Args:
            recommendations: List of recommended actions
            
        Returns:
            Dictionary containing implementation plan
        """
        # Sort recommendations by priority
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: x.get("priority", 100)  # Lower number = higher priority
        )
        
        # Generate phased implementation plan
        phases = {
            "immediate": {
                "timeframe": "Next 1-4 weeks",
                "actions": [],
                "description": "Focus on these high-impact changes that can be implemented quickly."
            },
            "short_term": {
                "timeframe": "Next 1-3 months",
                "actions": [],
                "description": "Build on initial changes with these additional actions."
            },
            "medium_term": {
                "timeframe": "Next 3-6 months",
                "actions": [],
                "description": "Once the foundation is established, incorporate these actions."
            },
            "long_term": {
                "timeframe": "Beyond 6 months",
                "actions": [],
                "description": "These actions complete the comprehensive approach to healthy aging."
            }
        }
        
        # Assign actions to phases based on priority and complexity
        for i, rec in enumerate(sorted_recommendations):
            action = rec["action"]
            
            # Simple, high-priority actions go in immediate phase
            if i < 2:
                phases["immediate"]["actions"].append({
                    "action": action,
                    "steps": self._generate_implementation_steps(action)
                })
            # Medium priority actions go in short term
            elif i < 4:
                phases["short_term"]["actions"].append({
                    "action": action,
                    "steps": self._generate_implementation_steps(action)
                })
            # Lower priority actions go in medium term
            elif i < 6:
                phases["medium_term"]["actions"].append({
                    "action": action,
                    "steps": self._generate_implementation_steps(action)
                })
            # Remaining actions go in long term
            else:
                phases["long_term"]["actions"].append({
                    "action": action,
                    "steps": self._generate_implementation_steps(action)
                })
        
        # Add monitoring and adjustment plan
        monitoring_plan = {
            "frequency": "Every 3 months",
            "metrics_to_track": [
                "Health markers (weight, blood pressure, energy levels)",
                "Lifestyle habits (physical activity, sleep, diet)",
                "Stress levels and mental well-being",
                "Progress on specific recommendations"
            ],
            "adjustment_approach": "Review progress and outcomes, identify successful strategies and challenges, and refine your approach as needed."
        }
        
        return {
            "phases": phases,
            "monitoring_plan": monitoring_plan,
            "success_factors": [
                "Consistency is more important than perfection",
                "Small, sustainable changes often lead to better long-term results than dramatic overhauls",
                "Social support significantly increases success rates for lifestyle changes",
                "Regular monitoring and adjustment keeps the plan relevant as circumstances change"
            ]
        }
    
    def _generate_implementation_steps(self, action: str) -> List[str]:
        """
        Generate implementation steps for a specific action
        
        Args:
            action: The recommended action
            
        Returns:
            List of implementation steps
        """
        action_lower = action.lower()
        
        # Physical activity implementation steps
        if "physical activity" in action_lower or "exercise" in action_lower:
            return [
                "Start with a health assessment or consult with a healthcare provider if you have any concerns",
                "Choose activities you enjoy to increase adherence",
                "Begin with 10-15 minute sessions and gradually increase duration",
                "Aim for a mix of aerobic, strength, flexibility, and balance exercises",
                "Track your activity using a journal, app, or wearable device",
                "Consider finding an exercise partner or group for accountability and social support"
            ]
        
        # Sleep improvement steps
        elif "sleep" in action_lower:
            return [
                "Establish a consistent sleep schedule with regular bed and wake times",
                "Create a relaxing bedtime routine (e.g., reading, gentle stretching, warm bath)",
                "Optimize your sleep environment (cool, dark, quiet, comfortable)",
                "Limit screen time and blue light exposure at least one hour before bed",
                "Avoid caffeine after noon and limit alcohol consumption",
                "Consider tracking sleep patterns to identify improvement opportunities"
            ]
        
        # Diet improvement steps
        elif "diet" in action_lower or "nutrition" in action_lower:
            return [
                "Conduct a baseline assessment of your current eating patterns",
                "Gradually increase vegetables and fruits to at least 5 servings daily",
                "Choose whole grains over refined grains when possible",
                "Include quality protein sources at each meal",
                "Minimize ultra-processed foods, added sugars, and excessive salt",
                "Practice mindful eating by paying attention to hunger cues and enjoying meals without distractions",
                "Consider consulting with a registered dietitian for personalized guidance"
            ]
        
        # Stress management steps
        elif "stress" in action_lower:
            return [
                "Identify your main sources of stress using a stress journal",
                "Learn and practice at least one relaxation technique (deep breathing, progressive muscle relaxation, or meditation)",
                "Start with 5 minutes daily and gradually increase to 15-20 minutes",
                "Incorporate physical activity, which helps reduce stress",
                "Establish clear boundaries between work and personal time",
                "Consider professional support if stress significantly impacts your wellbeing"
            ]
        
        # Financial planning steps
        elif "financial" in action_lower or "retirement" in action_lower:
            return [
                "Gather and organize your financial documents and information",
                "Create or update your budget to understand current cash flow",
                "Review your retirement savings and projected needs",
                "Assess your insurance coverage, especially health and long-term care",
                "Consider consulting with a financial advisor for personalized guidance",
                "Develop a written financial plan with specific goals and actions",
                "Schedule regular reviews to monitor progress and make adjustments"
            ]
        
        # Social connection steps
        elif "social" in action_lower or "connection" in action_lower:
            return [
                "Map your current social network and identify areas to strengthen or expand",
                "Schedule regular check-ins with important people in your life",
                "Identify activities or groups aligned with your interests",
                "Take initiative to organize social gatherings or outings",
                "Consider volunteering, which provides social connections and a sense of purpose",
                "Practice active listening and engagement in your interactions",
                "Be open to new connections across different age groups and backgrounds"
            ]
        
        # Generic implementation steps for other actions
        return [
            "Research to better understand the specific benefits and approaches",
            "Start with small, achievable changes",
            "Track your progress using appropriate metrics",
            "Build consistency before increasing intensity or complexity",
            "Seek professional guidance if needed",
            "Review and adjust your approach after 4-6 weeks"
        ]


# Factory function to create integration engine
def create_integration_engine(model_manager: ModelManager) -> IntegrationEngine:
    """Create an integration engine with the given model manager"""
    return IntegrationEngine(model_manager)

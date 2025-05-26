# prompts.py
# Constant branding intro text
BRANDING_INTRO = (
    "This audit identifies missed revenue opportunities in {brand_name}'s digital "
    "marketing funnel by analyzing gaps between its proven product advantages and "
    "current messaging effectiveness. "
    #We evaluate how unclear copy, underutilized "
    #"social proof, and inconsistent brand positioning dilute conversions—despite the "
    #"fence system's 99% success rate and 15+ years of market validation. Through "
    #"competitor benchmarking, SWOT alignment, and conversion-focused copy frameworks "
    #"(AIDA/FAB), we pinpoint where sharper audience targeting, benefit-driven storytelling, "
    #"and trust-building content can unlock significant growth."
)

# All prompts now expect "Website Description" instead of "Page Content"
SOP_PROMPTS = {
    "branding_messaging": (
        "In 1 short paragraph, describe the brand's unique messaging and positioning strategy based on the website description."
        #"Start with 'This audit identifies missed revenue opportunities in {brand_name}'s digital marketing funnel by analyzing gaps between its proven product advantages and current messaging effectiveness. "
        #"We evaluate how unclear copy, underutilized social proof, and inconsistent brand positioning dilute conversions—despite...'. "
        "All in just one paragraph. "
    ),
    "executive_summary": (
        "Explain the business in 1 line in bold. Don't use examples (e.g. ...). "
        "Based on the analysis Give 3 critical points to improve the website, followed by the statement 'Based on the analysis, here are the three critical copy and brand fixes:'. "
        "Format each point (as 1,2,3) as a separate 1 line paragraph."
        "Don't add any additional note. "
    ),
    "business_description": (
        "Explain what the business does to a 7th grader in 2 simple paragraphs without mentioning AI or using emojis."
    ),
    "revenue_model": (
        "Explain in 2 paragraphs how the business generates revenue, written simply for a 7th grader to understand. No emojis."
    ),
    "target_audience": (
        "Explain in 2 short paragraphs who the ideal target audience is for the marketing campaigns. Keep it 7th grader level, no emojis."
    ),
    "swot_analysis": (
        "Based on the business description, revenue model, and target audience, write a simple SWOT analysis in 4 points (Strengths, Weaknesses, Opportunities, Threats) for the business. "
        "Format each point as a separate paragraph with a bold heading followed by a short description (two lines only).Don't add any additional note"
    ),
    "porter_analysis": (
        "Based on the business description, revenue model, and target audience, write a simple Porter's 5 Forces in 5 points (Competitors, Threat of New Competitors , Threat of Substitutes , Supplier Power, Customer Power) for the business.Don't skip any point. "
        "Format each point as a separate paragraph with a bold heading followed by a very short description (one line only).Don't add any additional note"
    ),
    "ideal_copy_style": (
        "Among PAS, AIDA, FAB, 4Ps frameworks, recommend the best copywriting framework for the business based on website type. Explain choice simply without examples or emojis."
    ),
   
    "copy_gap_analysis": (

        "Assess the website copy for: Clarity of Structure, Emotional & Logical Persuasion, Relevance to Target Audience, Strong CTA Alignment, and Proof & Credibility Integration. "
        "Format each point as a separate paragraph with a bold heading followed by very short description(one line ony).After the 5 points, add a final score in this format:\n**Score**: X/10"
        "Don't add any additional note."
    ),

    "copy_suggestions": (
        "Suggest 3 actionable tips to improve the website copy in 1 line each. No examples or emojis."
        "Format each point as a separate one line paragraph."
    ),
    "brand_analysis": (
        "Provide a brief analysis of the brand's identity, mission, and core values based on the website description."
    ),
    "brand_visuals": (
        "Describe the brand's visual style based on fonts, colors, and imagery from the website. Keep it short and clear."
        "Format each point as a separate paragraph with a bold heading followed by a short description.Don't add any additional note"
    ),
    "brand_personality": (
        "Explain the brand's personality (tone, mood, attitude) as seen on the website, in 2 paragraphs, 7th grade level."
    ),
    "brand_positioning": (
        "Explain the brand positioning in 2 paragraphs. Compare current vs ideal positioning and explain gaps. No emojis."
    ),
    "recommendations": (
        "List top 3 recommendations to improve brand messaging, copy, and conversions.No emojis.Don't use examples."
        "Format each point as a separate paragraph with a bold 2-word heading followed by a short description (one line only). Don't add any additional note"
        
    )
}

"""
Metrics for evaluating voice agent conversations.

This module provides three core metrics:
1. Goal Completion - Did the agent achieve the conversation goal?
2. Conversational Quality - Was the conversation natural and appropriate?
3. Compliance - Did the agent follow legal and ethical guidelines?
"""

import re
from typing import Dict, Any, List, Tuple
from collections import Counter


class GoalCompletionMetric:
    """
    Evaluates whether the agent achieved the conversation goal.

    For debt collection:
    - Payment commitment (50 points)
    - Specific amount/date mentioned (25 points)
    - Follow-up action agreed (25 points)

    Total: 0-100 points
    """

    def __init__(self):
        self.name = "goal_completion"
        self.max_score = 100

        # Keywords indicating payment commitment
        self.commitment_keywords = [
            'i will pay', 'i\'ll pay', 'i can pay', 'i agree',
            'payment plan', 'set up', 'i\'ll send', 'i promise',
            'okay', 'sounds good', 'that works', 'deal', 'yes'
        ]

        # Keywords for specific amounts
        self.amount_keywords = [
            r'\$\d+', r'\d+ dollars', 'amount', 'payment of'
        ]

        # Keywords for dates/schedules
        self.date_keywords = [
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday', 'tomorrow', 'next week', 'this month',
            r'\d+th', r'\d+st', r'\d+nd', r'\d+rd', 'on the'
        ]

    def evaluate(self, transcript: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate goal completion from conversation transcript.

        Args:
            transcript: List of conversation turns
                       [{'speaker': 'agent', 'message': '...'}, ...]

        Returns:
            Dict with score and breakdown
        """
        # Extract user messages (persona responses)
        user_messages = [
            turn['message'].lower()
            for turn in transcript
            if turn['speaker'] == 'user'
        ]

        # Check for payment commitment (50 points)
        commitment_score = self._check_commitment(user_messages)

        # Check for specific amount/date (25 points)
        specifics_score = self._check_specifics(user_messages)

        # Check for follow-up action (25 points)
        followup_score = self._check_followup(user_messages)

        total_score = commitment_score + specifics_score + followup_score

        return {
            'score': total_score,
            'breakdown': {
                'commitment': commitment_score,
                'specifics': specifics_score,
                'followup': followup_score
            },
            'explanation': self._generate_explanation(
                commitment_score, specifics_score, followup_score
            )
        }

    def _check_commitment(self, user_messages: List[str]) -> float:
        """Check if user committed to payment (50 points)."""
        full_text = ' '.join(user_messages)

        # Count commitment indicators
        commitment_count = sum(
            1 for keyword in self.commitment_keywords
            if keyword in full_text
        )

        if commitment_count >= 2:
            return 50.0  # Strong commitment
        elif commitment_count == 1:
            return 35.0  # Weak commitment
        else:
            return 0.0   # No commitment

    def _check_specifics(self, user_messages: List[str]) -> float:
        """Check if specific amount/date mentioned (25 points)."""
        full_text = ' '.join(user_messages)

        # Check for amounts
        amount_found = any(
            re.search(pattern, full_text)
            for pattern in self.amount_keywords
        )

        # Check for dates
        date_found = any(
            keyword in full_text or re.search(keyword, full_text)
            for keyword in self.date_keywords
        )

        if amount_found and date_found:
            return 25.0  # Both specified
        elif amount_found or date_found:
            return 15.0  # One specified
        else:
            return 0.0   # Neither specified

    def _check_followup(self, user_messages: List[str]) -> float:
        """Check if follow-up action agreed (25 points)."""
        followup_keywords = [
            'call back', 'follow up', 'check in', 'remind me',
            'send', 'email', 'confirmation', 'will do'
        ]

        full_text = ' '.join(user_messages)

        followup_count = sum(
            1 for keyword in followup_keywords
            if keyword in full_text
        )

        if followup_count >= 1:
            return 25.0
        else:
            return 0.0

    def _generate_explanation(
        self,
        commitment: float,
        specifics: float,
        followup: float
    ) -> str:
        """Generate human-readable explanation."""
        parts = []

        if commitment >= 35:
            parts.append("✅ Payment commitment detected")
        else:
            parts.append("❌ No clear payment commitment")

        if specifics >= 15:
            parts.append("✅ Specific details provided")
        else:
            parts.append("❌ Missing specific amount/date")

        if followup > 0:
            parts.append("✅ Follow-up action agreed")
        else:
            parts.append("⚠️ No follow-up action")

        return " | ".join(parts)


class ConversationalQualityMetric:
    """
    Evaluates the quality of the conversation.

    Checks for:
    - No repetitions/loops (25 points)
    - No hallucinations (25 points) - basic version
    - Appropriate tone (25 points) - basic version
    - Natural flow (25 points)

    Total: 0-100 points
    """

    def __init__(self):
        self.name = "conversational_quality"
        self.max_score = 100

    def evaluate(self, transcript: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate conversational quality.

        Args:
            transcript: List of conversation turns

        Returns:
            Dict with score and breakdown
        """
        agent_messages = [
            turn['message']
            for turn in transcript
            if turn['speaker'] == 'agent'
        ]

        # Check for repetitions (25 points)
        repetition_score = self._check_repetitions(agent_messages)

        # Check for hallucinations - basic (25 points)
        hallucination_score = self._check_hallucinations(agent_messages)

        # Check tone appropriateness - basic (25 points)
        tone_score = self._check_tone(agent_messages)

        # Check conversation flow (25 points)
        flow_score = self._check_flow(transcript)

        total_score = (
            repetition_score +
            hallucination_score +
            tone_score +
            flow_score
        )

        return {
            'score': total_score,
            'breakdown': {
                'no_repetitions': repetition_score,
                'no_hallucinations': hallucination_score,
                'appropriate_tone': tone_score,
                'natural_flow': flow_score
            },
            'explanation': self._generate_explanation(
                repetition_score, hallucination_score, tone_score, flow_score
            )
        }

    def _check_repetitions(self, agent_messages: List[str]) -> float:
        """Check for repetitive messages (25 points if no repetitions)."""
        if len(agent_messages) < 2:
            return 25.0

        # Check for exact duplicates
        unique_messages = len(set(agent_messages))
        total_messages = len(agent_messages)

        if unique_messages == total_messages:
            # No exact duplicates - check for similar phrases
            # Use simple n-gram overlap
            repetition_ratio = self._calculate_repetition_ratio(agent_messages)

            if repetition_ratio < 0.3:
                return 25.0  # Low repetition
            elif repetition_ratio < 0.5:
                return 15.0  # Medium repetition
            else:
                return 5.0   # High repetition
        else:
            # Has exact duplicates
            duplicate_ratio = 1 - (unique_messages / total_messages)
            return max(0, 25 * (1 - duplicate_ratio * 2))

    def _calculate_repetition_ratio(self, messages: List[str]) -> float:
        """Calculate how much repetition exists in messages."""
        if len(messages) < 2:
            return 0.0

        # Simple approach: compare adjacent messages
        repetitions = 0
        for i in range(len(messages) - 1):
            msg1_words = set(messages[i].lower().split())
            msg2_words = set(messages[i + 1].lower().split())

            if msg1_words and msg2_words:
                overlap = len(msg1_words & msg2_words) / len(msg1_words | msg2_words)
                if overlap > 0.5:
                    repetitions += 1

        return repetitions / (len(messages) - 1) if len(messages) > 1 else 0.0

    def _check_hallucinations(self, agent_messages: List[str]) -> float:
        """
        Basic check for hallucinations (25 points).

        In a simple version, we check for obviously false statements.
        In Phase 4, we'll use LLM-as-judge for better detection.
        """
        # For now, give full points (will enhance with LLM judge)
        # Basic check: look for contradictions or nonsense

        problematic_patterns = [
            'as an ai', 'i am an ai', 'i cannot', 'i\'m not able to',
            'i don\'t have access', 'i apologize for the confusion'
        ]

        full_text = ' '.join(agent_messages).lower()

        issues_found = sum(
            1 for pattern in problematic_patterns
            if pattern in full_text
        )

        if issues_found == 0:
            return 25.0
        elif issues_found <= 2:
            return 15.0
        else:
            return 5.0

    def _check_tone(self, agent_messages: List[str]) -> float:
        """
        Basic tone check (25 points).

        Checks for professional, empathetic language.
        """
        positive_tone_words = [
            'understand', 'help', 'support', 'appreciate', 'thank',
            'sorry', 'apologize', 'together', 'work with you'
        ]

        negative_tone_words = [
            'must', 'have to', 'need to', 'required', 'mandatory',
            'immediately', 'urgent', 'demand'
        ]

        full_text = ' '.join(agent_messages).lower()

        positive_count = sum(
            1 for word in positive_tone_words
            if word in full_text
        )

        negative_count = sum(
            1 for word in negative_tone_words
            if word in full_text
        )

        # Good tone has more positive than negative
        if positive_count > negative_count * 2:
            return 25.0
        elif positive_count > negative_count:
            return 18.0
        else:
            return 10.0

    def _check_flow(self, transcript: List[Dict[str, str]]) -> float:
        """
        Check conversation flow (25 points).

        Good flow: appropriate turn lengths, responsive to user.
        """
        if len(transcript) < 4:
            return 25.0  # Too short to judge

        # Check turn lengths are reasonable (not too long/short)
        turn_lengths = [
            len(turn['message'].split())
            for turn in transcript
            if turn['speaker'] == 'agent'
        ]

        avg_length = sum(turn_lengths) / len(turn_lengths)

        # Ideal: 10-40 words per turn
        if 10 <= avg_length <= 40:
            return 25.0
        elif 5 <= avg_length <= 60:
            return 18.0
        else:
            return 10.0

    def _generate_explanation(
        self,
        repetition: float,
        hallucination: float,
        tone: float,
        flow: float
    ) -> str:
        """Generate explanation."""
        parts = []

        parts.append(f"Repetitions: {repetition:.0f}/25")
        parts.append(f"Hallucinations: {hallucination:.0f}/25")
        parts.append(f"Tone: {tone:.0f}/25")
        parts.append(f"Flow: {flow:.0f}/25")

        return " | ".join(parts)


class ComplianceMetric:
    """
    Evaluates compliance with debt collection regulations.

    Checks for:
    - No threats (critical)
    - No illegal language (critical)
    - Privacy respected (critical)
    - Professional communication (important)

    Total: 0-100 points (or FAIL if critical violation)
    """

    def __init__(self):
        self.name = "compliance"
        self.max_score = 100

        # Critical violations (instant fail)
        self.threat_keywords = [
            'sue', 'lawsuit', 'legal action', 'arrest', 'jail',
            'garnish', 'seize', 'repossess', 'threaten'
        ]

        self.illegal_keywords = [
            'must pay now', 'pay immediately or', 'consequences will be',
            'you have no choice', 'we will ruin'
        ]

        # Privacy violations
        self.privacy_keywords = [
            'told your employer', 'contacted your family',
            'public record', 'shared your information'
        ]

        # Unprofessional language
        self.unprofessional_keywords = [
            'stupid', 'idiot', 'lazy', 'deadbeat', 'loser',
            'pathetic', 'irresponsible'
        ]

    def evaluate(self, transcript: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate compliance.

        Args:
            transcript: List of conversation turns

        Returns:
            Dict with score, violations, and pass/fail status
        """
        agent_messages = [
            turn['message'].lower()
            for turn in transcript
            if turn['speaker'] == 'agent'
        ]

        full_text = ' '.join(agent_messages)

        # Check for critical violations
        violations = []

        # Threats (critical - 0 points if found)
        threat_violations = [
            keyword for keyword in self.threat_keywords
            if keyword in full_text
        ]
        if threat_violations:
            violations.append(f"CRITICAL: Threats detected - {threat_violations}")

        # Illegal language (critical)
        illegal_violations = [
            keyword for keyword in self.illegal_keywords
            if keyword in full_text
        ]
        if illegal_violations:
            violations.append(f"CRITICAL: Illegal language - {illegal_violations}")

        # Privacy violations (critical)
        privacy_violations = [
            keyword for keyword in self.privacy_keywords
            if keyword in full_text
        ]
        if privacy_violations:
            violations.append(f"CRITICAL: Privacy violation - {privacy_violations}")

        # Unprofessional language (serious but not critical)
        unprofessional_violations = [
            keyword for keyword in self.unprofessional_keywords
            if keyword in full_text
        ]
        if unprofessional_violations:
            violations.append(f"SERIOUS: Unprofessional language - {unprofessional_violations}")

        # Calculate score
        critical_violations = len(threat_violations) + len(illegal_violations) + len(privacy_violations)

        if critical_violations > 0:
            score = 0.0  # Fail
            passed = False
        elif unprofessional_violations:
            score = 60.0  # Serious issue but not critical
            passed = True
        else:
            score = 100.0  # Passed
            passed = True

        return {
            'score': score,
            'passed': passed,
            'violations': violations,
            'breakdown': {
                'threats': len(threat_violations),
                'illegal_language': len(illegal_violations),
                'privacy_violations': len(privacy_violations),
                'unprofessional': len(unprofessional_violations)
            },
            'explanation': self._generate_explanation(violations, passed)
        }

    def _generate_explanation(self, violations: List[str], passed: bool) -> str:
        """Generate explanation."""
        if not violations:
            return "✅ No compliance issues detected"
        elif not passed:
            return f"❌ FAILED - Critical violations: {len(violations)}"
        else:
            return f"⚠️ PASSED with warnings: {len(violations)} issues"

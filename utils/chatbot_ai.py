import re
from datetime import datetime, date
from models.exam import Exam


class ChatbotAI:
    """AI-powered chatbot for exam management with natural language processing."""

    CATEGORY_KEYWORDS = {
        'Banking': ['sbi', 'ibps', 'rbi', 'bank', 'banking', 'nabard', 'sebi', 'lic', 'niacl'],
        'SSC': ['ssc', 'cgl', 'chsl', 'mts', 'stenographer', 'staff selection'],
        'UPSC': ['upsc', 'ias', 'ips', 'civil service', 'civil services', 'cse', 'nda', 'cds', 'capf'],
        'TNPSC': ['tnpsc', 'tamil nadu', 'tn psc', 'group 1', 'group 2', 'group 4', 'vao'],
        'Railway': ['railway', 'rrb', 'ntpc', 'alp', 'group d', 'je railway', 'rpf'],
        'Group': ['group exam', 'group a', 'group b', 'group c']
    }

    HELP_TEXT = """🤖 **ExamTrack AI Assistant** — Here's what I can do:

📝 **Add an exam:**
  • "Add SBI PO exam on 2026-08-15 deadline 2026-07-01"
  • "Add UPSC CSE Prelims"

🔍 **Search exams:**
  • "Search banking exams"
  • "Find SBI PO"
  • "Show all exams"

📅 **Upcoming exams:**
  • "Show upcoming exams"
  • "What's next?"

📊 **Statistics:**
  • "Show stats"
  • "Summary"

🗑️ **Delete exam:**
  • "Delete SBI PO"

💡 **Tips:**
  • "Tips for UPSC preparation"

Just type naturally — I'll understand! 😊"""

    def process_message(self, message, db_session):
        """Process a user message and return an appropriate response."""
        msg = message.lower().strip()

        # Detect intent
        if any(word in msg for word in ['help', 'commands', 'what can you do', 'how to use']):
            return self._help_response()

        if any(word in msg for word in ['add ', 'create ', 'new exam']):
            return self._add_exam(message, db_session)

        if any(word in msg for word in ['search ', 'find ', 'show all', 'list ', 'show exam']):
            return self._search_exams(message, db_session)

        if any(word in msg for word in ['upcoming', 'next exam', "what's next", 'whats next', 'nearest']):
            return self._upcoming_exams(db_session)

        if any(word in msg for word in ['delete ', 'remove ']):
            return self._delete_exam(message, db_session)

        if any(word in msg for word in ['stats', 'statistics', 'summary', 'count', 'how many']):
            return self._stats(db_session)

        if any(word in msg for word in ['tip', 'advice', 'prepare', 'preparation', 'strategy']):
            return self._tips(message)

        if any(word in msg for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return {
                'response': "👋 Hello! I'm your ExamTrack AI assistant. Type **help** to see what I can do!",
                'type': 'info'
            }

        # Default
        return {
            'response': f"🤔 I'm not sure what you mean by \"{message}\". Type **help** to see available commands!",
            'type': 'info'
        }

    def _help_response(self):
        return {'response': self.HELP_TEXT, 'type': 'info'}

    def _detect_category(self, text):
        """Detect exam category from text."""
        text_lower = text.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        return 'Banking'  # Default

    def _add_exam(self, message, db_session):
        """Parse and add an exam from natural language."""
        try:
            # Extract exam name — remove command words
            name_text = re.sub(
                r'^(add|create|new exam)\s+', '', message, flags=re.IGNORECASE
            ).strip()

            # Extract dates
            date_match = re.search(
                r'(?:on|date|exam date)\s+(\d{4}-\d{2}-\d{2})', message, re.IGNORECASE
            )
            deadline_match = re.search(
                r'(?:deadline|last date|apply by)\s+(\d{4}-\d{2}-\d{2})', message, re.IGNORECASE
            )

            # Clean name (remove date parts)
            clean_name = re.sub(
                r'\s*(on|date|exam date|deadline|last date|apply by)\s+\d{4}-\d{2}-\d{2}',
                '', name_text, flags=re.IGNORECASE
            ).strip()

            if not clean_name:
                return {
                    'response': '❌ Please provide an exam name. Example: "Add SBI PO exam on 2026-08-15"',
                    'type': 'error'
                }

            # Detect category
            category = self._detect_category(clean_name)

            # Parse dates
            exam_date = None
            deadline = None
            if date_match:
                try:
                    exam_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                except ValueError:
                    pass
            if deadline_match:
                try:
                    deadline = datetime.strptime(deadline_match.group(1), '%Y-%m-%d').date()
                except ValueError:
                    pass

            # Create exam
            exam = Exam(
                name=clean_name,
                category=category,
                exam_date=exam_date,
                application_deadline=deadline,
                status='Upcoming',
                priority='Medium'
            )
            db_session.add(exam)
            db_session.commit()

            response = f"✅ **Exam Added Successfully!**\n\n"
            response += f"📝 **Name:** {clean_name}\n"
            response += f"📂 **Category:** {category}\n"
            if exam_date:
                response += f"📅 **Exam Date:** {exam_date.strftime('%B %d, %Y')}\n"
            if deadline:
                response += f"⏰ **Deadline:** {deadline.strftime('%B %d, %Y')}\n"
            response += f"\nYou can edit more details from the Exams page."

            return {'response': response, 'type': 'success', 'data': exam.to_dict()}

        except Exception as e:
            db_session.rollback()
            return {
                'response': f'❌ Error adding exam: {str(e)}. Try: "Add SBI PO exam on 2026-08-15"',
                'type': 'error'
            }

    def _search_exams(self, message, db_session):
        """Search exams by name or category."""
        search_text = re.sub(
            r'^(search|find|show all|list|show exam[s]?)\s*', '', message, flags=re.IGNORECASE
        ).strip()

        query = db_session.query(Exam)

        if search_text:
            query = query.filter(
                Exam.name.ilike(f'%{search_text}%') |
                Exam.category.ilike(f'%{search_text}%')
            )

        exams = query.order_by(Exam.exam_date.asc().nullslast()).limit(10).all()

        if not exams:
            return {
                'response': f'🔍 No exams found matching "{search_text}". Try adding one with "Add [exam name]"!',
                'type': 'info'
            }

        response = f"🔍 **Found {len(exams)} exam(s):**\n\n"
        for exam in exams:
            emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(exam.priority, '⚪')
            date_str = exam.exam_date.strftime('%b %d, %Y') if exam.exam_date else 'TBD'
            response += f"{emoji} **{exam.name}** — {exam.category} | {date_str} | {exam.status}\n"

        return {
            'response': response,
            'type': 'list',
            'data': [e.to_dict() for e in exams]
        }

    def _upcoming_exams(self, db_session):
        """Show upcoming exams."""
        today = date.today()
        exams = db_session.query(Exam).filter(
            Exam.exam_date >= today,
            Exam.status.in_(['Upcoming', 'Applied', 'Scheduled'])
        ).order_by(Exam.exam_date.asc()).limit(5).all()

        if not exams:
            return {
                'response': '📅 No upcoming exams found. Add one using "Add [exam name]"!',
                'type': 'info'
            }

        response = "📅 **Upcoming Exams:**\n\n"
        for exam in exams:
            days_left = (exam.exam_date - today).days
            urgency = '🔥' if days_left <= 7 else '⏰' if days_left <= 30 else '📌'
            response += f"{urgency} **{exam.name}** — {exam.exam_date.strftime('%b %d, %Y')} ({days_left} days left)\n"

        return {
            'response': response,
            'type': 'list',
            'data': [e.to_dict() for e in exams]
        }

    def _delete_exam(self, message, db_session):
        """Delete an exam by name."""
        name_text = re.sub(
            r'^(delete|remove)\s+', '', message, flags=re.IGNORECASE
        ).strip()

        if not name_text:
            return {
                'response': '❌ Please specify which exam to delete. Example: "Delete SBI PO"',
                'type': 'error'
            }

        exam = db_session.query(Exam).filter(
            Exam.name.ilike(f'%{name_text}%')
        ).first()

        if not exam:
            return {
                'response': f'🔍 No exam found matching "{name_text}".',
                'type': 'error'
            }

        exam_name = exam.name
        db_session.delete(exam)
        db_session.commit()

        return {
            'response': f'🗑️ **Deleted:** {exam_name} has been removed successfully.',
            'type': 'success'
        }

    def _stats(self, db_session):
        """Show exam statistics."""
        total = db_session.query(Exam).count()
        upcoming = db_session.query(Exam).filter(Exam.status == 'Upcoming').count()
        high = db_session.query(Exam).filter(Exam.priority == 'High').count()

        cat_counts = []
        for cat in Exam.CATEGORIES:
            count = db_session.query(Exam).filter(Exam.category == cat).count()
            if count > 0:
                cat_counts.append(f"  • {cat}: {count}")

        response = f"📊 **Exam Statistics:**\n\n"
        response += f"📝 Total Exams: **{total}**\n"
        response += f"📅 Upcoming: **{upcoming}**\n"
        response += f"🔴 High Priority: **{high}**\n"
        if cat_counts:
            response += f"\n📂 **By Category:**\n" + "\n".join(cat_counts)

        return {'response': response, 'type': 'info'}

    def _tips(self, message):
        """Provide exam preparation tips."""
        tips = {
            'upsc': "📚 **UPSC Tips:**\n• Start with NCERT books (6-12)\n• Read The Hindu daily\n• Practice answer writing\n• Make short notes\n• Join a test series\n• Revise regularly",
            'ssc': "📚 **SSC Tips:**\n• Focus on Quant & English\n• Practice previous year papers\n• Learn shortcuts for calculations\n• Improve typing speed for DEO\n• Take mock tests weekly",
            'banking': "📚 **Banking Tips:**\n• Master Quant & Reasoning\n• Stay updated with current affairs\n• Practice DI & puzzles daily\n• Learn banking awareness\n• Attempt sectional tests",
            'tnpsc': "📚 **TNPSC Tips:**\n• Study Tamil Nadu history & culture\n• Read Samacheer Kalvi textbooks\n• Practice previous year questions\n• Focus on current affairs (TN specific)\n• Join TNPSC study groups",
            'railway': "📚 **Railway Tips:**\n• Focus on General Science\n• Practice Mathematics shortcuts\n• Study GK & Current Affairs\n• Solve RRB previous papers\n• Focus on speed & accuracy",
        }

        msg_lower = message.lower()
        for key, tip in tips.items():
            if key in msg_lower:
                return {'response': tip, 'type': 'info'}

        general = "📚 **General Exam Tips:**\n• Create a study schedule\n• Practice mock tests regularly\n• Revise consistently\n• Stay updated with current affairs\n• Take care of health & sleep\n• Join study groups for motivation"
        return {'response': general, 'type': 'info'}

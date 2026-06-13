from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from groq import Groq
from django.conf import settings
from .models import Resume, Experience
from .serializers import ResumeSerializer, ResumeCreateSerializer
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from rest_framework_simplejwt.authentication import JWTAuthentication


# ── List + Create Resumes ─────────────────────────────
class ResumeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResumeCreateSerializer
        return ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ── Get + Delete Single Resume ────────────────────────
class ResumeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class   = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


# ── Generate AI Content ───────────────────────────────
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_resume_ai(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        # build experience text
        experiences = resume.experience.all()
        exp_text = '\n'.join([
            f"- {exp.role} at {exp.company} ({exp.start_date} to {exp.end_date}): {exp.description}"
            for exp in experiences
        ])

        # build skills text
        skills = resume.skills.all()
        skills_text = ', '.join([f"{s.category}: {s.items}" for s in skills])

        # build education text
        education = resume.education.all()
        edu_text = '\n'.join([
            f"- {edu.degree} from {edu.institution} ({edu.year})"
            for edu in education
        ])

        prompt = f"""
You are an expert ATS-optimized resume writer.

Candidate Information:
Name: {resume.full_name}
Target Role: {resume.target_role}
Skills: {skills_text}
Experience:
{exp_text}
Education:
{edu_text}
Job Description: {resume.job_description}

Tasks:
1. Write a compelling 3-4 line professional summary optimized for ATS. Include relevant keywords from the job description.
2. For each experience entry, write 3 ATS-friendly bullet points starting with strong action verbs. Include metrics where possible.
3. Give an ATS match score out of 100 based on how well the candidate matches the job description.

Format your response EXACTLY like this:
SUMMARY:
[summary here]

EXPERIENCE_BULLETS:
[Company Name - Role]:
- [bullet 1]
- [bullet 2]
- [bullet 3]

ATS_SCORE:
[number only, e.g. 78]
"""
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': prompt}]
        )

        content = response.choices[0].message.content

        # parse summary
        summary = ''
        if 'SUMMARY:' in content:
            summary_part = content.split('SUMMARY:')[1]
            if 'EXPERIENCE_BULLETS:' in summary_part:
                summary = summary_part.split('EXPERIENCE_BULLETS:')[0].strip()
            else:
                summary = summary_part.strip()

        # parse ATS score
        ats_score = 0
        if 'ATS_SCORE:' in content:
            score_text = content.split('ATS_SCORE:')[1].strip()
            digits = ''.join(filter(str.isdigit, score_text[:5]))
            ats_score = int(digits) if digits else 0

        # parse experience bullets and save
        if 'EXPERIENCE_BULLETS:' in content:
            bullets_section = content.split('EXPERIENCE_BULLETS:')[1]
            if 'ATS_SCORE:' in bullets_section:
                bullets_section = bullets_section.split('ATS_SCORE:')[0]

            for exp in experiences:
                search_key = f"{exp.company} - {exp.role}"
                if search_key in bullets_section:
                    start = bullets_section.index(search_key) + len(search_key)
                    end   = bullets_section.find('\n\n', start)
                    bullets = bullets_section[start:end if end != -1 else None].strip()
                    exp.ai_bullets = bullets
                    exp.save()

        # save to resume
        resume.summary   = summary
        resume.ats_score = ats_score
        resume.save()

        return Response({
            'summary':   summary,
            'ats_score': ats_score,
            'message':   'AI content generated successfully'
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ── Download PDF ──────────────────────────────────────
def generate_pdf(request, pk):
    # manually authenticate using JWT token from query param
    token = request.GET.get('token', '')
    if not token:
        return HttpResponse('Unauthorized — no token provided', status=401)

    jwt_auth = JWTAuthentication()
    try:
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except Exception:
        return HttpResponse('Unauthorized — invalid token', status=401)

    resume = get_object_or_404(Resume, pk=pk, user=user)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        'Name',
        fontSize=20,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor('#1a1a2e')
    )
    contact_style = ParagraphStyle(
        'Contact',
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor('#555555')
    )
    section_style = ParagraphStyle(
        'Section',
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor('#1a1a2e'),
        borderPad=0
    )
    body_style = ParagraphStyle(
        'Body',
        fontSize=9.5,
        fontName='Helvetica',
        spaceAfter=3,
        leading=14,
        textColor=colors.HexColor('#333333')
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        fontSize=9.5,
        fontName='Helvetica',
        spaceAfter=2,
        leading=14,
        leftIndent=12,
        textColor=colors.HexColor('#333333')
    )
    job_title_style = ParagraphStyle(
        'JobTitle',
        fontSize=10,
        fontName='Helvetica-Bold',
        spaceAfter=1,
        textColor=colors.HexColor('#1a1a2e')
    )
    date_style = ParagraphStyle(
        'Date',
        fontSize=9,
        fontName='Helvetica-Oblique',
        spaceAfter=4,
        textColor=colors.HexColor('#777777')
    )

    story = []

    # ── Header ───────────────────────────────────────
    story.append(Paragraph(resume.full_name, name_style))

    contact_parts = []
    if resume.email:    contact_parts.append(resume.email)
    if resume.phone:    contact_parts.append(resume.phone)
    if resume.location: contact_parts.append(resume.location)
    if contact_parts:
        story.append(Paragraph(' | '.join(contact_parts), contact_style))

    link_parts = []
    if resume.linkedin: link_parts.append(resume.linkedin)
    if resume.github:   link_parts.append(resume.github)
    if link_parts:
        story.append(Paragraph(' | '.join(link_parts), contact_style))

    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#1a1a2e'), spaceAfter=8))

    # ── Summary ──────────────────────────────────────
    if resume.summary:
        story.append(Paragraph('PROFESSIONAL SUMMARY', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=6))
        story.append(Paragraph(resume.summary, body_style))

    # ── Experience ───────────────────────────────────
    experiences = resume.experience.all()
    if experiences:
        story.append(Paragraph('WORK EXPERIENCE', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=6))

        for exp in experiences:
            story.append(Paragraph(f"{exp.role} — {exp.company}", job_title_style))
            story.append(Paragraph(f"{exp.start_date} – {exp.end_date}", date_style))

            if exp.ai_bullets:
                for line in exp.ai_bullets.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        # normalize to bullet character
                        clean = line.lstrip('-•').strip()
                        story.append(Paragraph(f"• {clean}", bullet_style))
            elif exp.description:
                story.append(Paragraph(exp.description, body_style))

            story.append(Spacer(1, 4))

    # ── Skills ───────────────────────────────────────
    skills = resume.skills.all()
    if skills:
        story.append(Paragraph('SKILLS', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=6))

        for skill in skills:
            story.append(Paragraph(f"<b>{skill.category}:</b> {skill.items}", body_style))

    # ── Education ────────────────────────────────────
    education = resume.education.all()
    if education:
        story.append(Paragraph('EDUCATION', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=6))

        for edu in education:
            story.append(Paragraph(f"{edu.degree} — {edu.institution}", job_title_style))
            grade = f" | {edu.grade}" if edu.grade else ""
            story.append(Paragraph(f"{edu.year}{grade}", date_style))

    doc.build(story)

    buffer.seek(0)
    filename = f"{resume.full_name.replace(' ', '_')}_Resume.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
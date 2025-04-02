from django.db import models

class CandidateProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    skills = models.JSONField(default=list)  # Use default=list for empty JSON arrays
    education = models.JSONField(default=list)
    work_experience = models.JSONField(default=list)
    resume_file = models.FileField(upload_to="resumes/")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    required_skills = models.JSONField()
    description = models.TextField()

    def __str__(self):
        return self.title

class JobMatch(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    match_score = models.IntegerField()
    missing_skills = models.JSONField()
    summary = models.TextField()

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title} ({self.match_score}%)"

class CoverLetter(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cover Letter: {self.candidate.name} - {self.job.title}"

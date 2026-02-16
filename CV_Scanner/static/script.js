document.getElementById('cv_file').addEventListener('change', function(e) {
    const fileLabel = document.getElementById('fileLabel');
    if (e.target.files.length > 0) {
        fileLabel.textContent = e.target.files[0].name;
    } else {
        fileLabel.textContent = 'Upload Resume (PDF)';
    }
});

document.getElementById('scanForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    
    // Hide previous results and errors
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.textContent = 'Analyzing...';
    loader.style.display = 'inline-block';
    
    const formData = new FormData();
    formData.append('cv_file', document.getElementById('cv_file').files[0]);
    formData.append('job_description', document.getElementById('job_description').value);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'An error occurred during analysis');
        }
    } catch (error) {
        showError('Failed to connect to server. Please try again.');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.textContent = 'Analyze Resume';
        loader.style.display = 'none';
    }
});

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    // Update match score
    const matchScore = data.match_percentage;
    document.getElementById('matchScore').textContent = matchScore.toFixed(0) + '%';
    
    // Animate circular progress
    const circle = document.getElementById('scoreCircle');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (matchScore / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    
    // Update color based on score
    if (matchScore >= 70) {
        circle.style.stroke = '#10b981'; // green
    } else if (matchScore >= 50) {
        circle.style.stroke = '#f59e0b'; // orange
    } else {
        circle.style.stroke = '#ef4444'; // red
    }
    
    // Update stats
    document.getElementById('totalCvSkills').textContent = data.total_cv_skills;
    document.getElementById('totalJdSkills').textContent = data.total_jd_skills;
    document.getElementById('matchingSkillsCount').textContent = data.matching_skills.length;
    document.getElementById('missingSkillsCount').textContent = data.missing_skills.length;
    
    // Display matching skills
    const matchingSkillsDiv = document.getElementById('matchingSkills');
    matchingSkillsDiv.innerHTML = '';
    if (data.matching_skills.length > 0) {
        data.matching_skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag matching';
            tag.textContent = skill;
            matchingSkillsDiv.appendChild(tag);
        });
    } else {
        matchingSkillsDiv.innerHTML = '<p style="color: #94a3b8;">No matching skills found</p>';
    }
    
    // Display missing skills
    const missingSkillsDiv = document.getElementById('missingSkills');
    missingSkillsDiv.innerHTML = '';
    if (data.missing_skills.length > 0) {
        data.missing_skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag missing';
            tag.textContent = skill;
            missingSkillsDiv.appendChild(tag);
        });
    } else {
        missingSkillsDiv.innerHTML = '<p style="color: #94a3b8;">No missing skills - Perfect match!</p>';
    }
    
    // Show results
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('scanForm').reset();
    document.getElementById('fileLabel').textContent = 'Upload Resume (PDF)';
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    
    // Reset circular progress
    const circle = document.getElementById('scoreCircle');
    circle.style.strokeDashoffset = 565.48;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
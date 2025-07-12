const crypto = require('crypto');

// API configuration from frontend .env.local
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'yQ1sz7kmNo35R94vlMx3mw';
const API_SECRET = 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24';

// Generate HMAC signature like the frontend does
function generateSignature(apiKey, timestamp, body) {
    const message = `${apiKey}\n${timestamp}\n${body}`;
    const signature = crypto.createHmac('sha256', API_SECRET).update(message).digest('base64');
    return signature;
}

// Generate timestamp
function generateTimestamp() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// Test complete workflow
async function testCompleteWorkflow() {
    console.log('🚀 Testing Complete Frontend-Backend Workflow');
    console.log('=' .repeat(60));

    // Step 1: Start Analysis
    console.log('\n📋 Step 1: Starting Job Analysis...');
    
    const formData = new FormData();
    formData.append('job_description', 'Senior Full Stack Developer position at TechCorp. We are looking for an experienced developer with React, Node.js, and cloud experience to join our dynamic team.');
    formData.append('resume_text', `John Doe
Senior Software Engineer

EXPERIENCE:
• 6 years full-stack development experience
• Expert in React, TypeScript, and modern JavaScript
• Strong backend development with Node.js and Express
• Database experience with MongoDB and PostgreSQL
• Cloud deployment experience with AWS and Docker
• Led development teams of 4-6 engineers

SKILLS:
JavaScript, TypeScript, React, Node.js, Express, MongoDB, PostgreSQL, AWS, Docker, Git, Agile methodologies

EDUCATION:
Bachelor of Computer Science, Tech University (2017)`);
    formData.append('tone', 'professional');
    formData.append('focus_areas', 'relevant experience,technical skills,leadership experience');
    formData.append('include_salary_guidance', 'true');
    formData.append('include_interview_prep', 'true');

    const bodyForSignature = '';
    const timestamp = generateTimestamp();
    const signature = generateSignature(API_KEY, timestamp, bodyForSignature);

    try {
        const analysisResponse = await fetch(`${API_BASE_URL}/api/v1/analyze-application`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'X-Timestamp': timestamp,
                'X-Signature': signature,
            },
            body: formData
        });

        if (!analysisResponse.ok) {
            const errorData = await analysisResponse.json();
            console.log('❌ Analysis failed:', errorData);
            return;
        }

        const analysis = await analysisResponse.json();
        console.log('✅ Analysis started successfully!');
        console.log(`📋 Session ID: ${analysis.session_id}`);
        console.log(`📊 Status: ${analysis.status}`);
        console.log(`📈 Current Step: ${analysis.progress.current_step.step_name}`);

        const sessionId = analysis.session_id;

        // Step 2: Monitor Progress
        console.log('\n⏱️ Step 2: Monitoring Progress...');
        let completed = false;
        let attempts = 0;
        const maxAttempts = 30; // 5 minutes max

        while (!completed && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
            attempts++;

            // Get progress
            const progressTimestamp = generateTimestamp();
            const progressSignature = generateSignature(API_KEY, progressTimestamp, '');

            try {
                const progressResponse = await fetch(`${API_BASE_URL}/api/v1/analysis/${sessionId}/progress`, {
                    headers: {
                        'X-API-Key': API_KEY,
                        'X-Timestamp': progressTimestamp,
                        'X-Signature': progressSignature,
                    }
                });

                if (progressResponse.ok) {
                    const progress = await progressResponse.json();
                    console.log(`📈 Progress Update (${attempts}/30):`);
                    console.log(`   Step: ${progress.current_step.step_name}`);
                    console.log(`   Status: ${progress.current_step.status}`);
                    console.log(`   Overall: ${progress.overall_progress}%`);

                    if (progress.status === 'completed') {
                        completed = true;
                        console.log('✅ Analysis completed!');
                    } else if (progress.status === 'failed') {
                        console.log('❌ Analysis failed:', progress.error);
                        return;
                    }
                } else {
                    console.log(`⚠️ Progress check failed: ${progressResponse.status}`);
                }
            } catch (error) {
                console.log(`⚠️ Progress check error: ${error.message}`);
            }
        }

        if (!completed) {
            console.log('⏰ Analysis timed out after 5 minutes');
            return;
        }

        // Step 3: Get Results
        console.log('\n📄 Step 3: Retrieving Results...');
        
        const resultsTimestamp = generateTimestamp();
        const resultsSignature = generateSignature(API_KEY, resultsTimestamp, '');

        try {
            const resultsResponse = await fetch(`${API_BASE_URL}/api/v1/analysis/${sessionId}/results`, {
                headers: {
                    'X-API-Key': API_KEY,
                    'X-Timestamp': resultsTimestamp,
                    'X-Signature': resultsSignature,
                }
            });

            if (resultsResponse.ok) {
                const results = await resultsResponse.json();
                console.log('✅ Results retrieved successfully!');
                console.log('\n📊 Analysis Results Summary:');
                console.log(`🎯 Job Match Score: ${results.job_analysis?.match_score || 'N/A'}`);
                console.log(`📝 Resume Recommendations: ${results.resume_recommendations?.suggestions?.length || 0} suggestions`);
                console.log(`✉️ Cover Letter Generated: ${results.cover_letter ? 'Yes' : 'No'}`);
                console.log(`🎯 Skills Analysis: ${results.skills_analysis ? 'Complete' : 'Incomplete'}`);
                
                // Show a sample of the cover letter
                if (results.cover_letter?.content) {
                    console.log('\n📬 Cover Letter Preview:');
                    console.log(results.cover_letter.content.substring(0, 200) + '...');
                }

                console.log('\n🎉 Complete workflow test successful!');
            } else {
                console.log('❌ Failed to retrieve results:', resultsResponse.status);
            }
        } catch (error) {
            console.log('❌ Results retrieval error:', error.message);
        }

    } catch (error) {
        console.log('❌ Workflow error:', error.message);
    }
}

// Run the test
testCompleteWorkflow().catch(console.error);
// Global variables
// let currentUser = null;
// let allJobs = [];

// DOM Ready event
// document.addEventListener('DOMContentLoaded', function() {
//     // Check which page we're on
//     const path = window.location.pathname;
    
//     // Load current user data if logged in
//     if (document.querySelector('.navbar')) {
//         fetchCurrentUser();
//     }
    
//     // Handle specific page functionality
//     if (path.includes('/all_jobs')) {
//         loadAllJobs();
//     } else if (path.includes('/job_recommendations')) {
//         loadJobRecommendations();
//     } else if (path.includes('/job_compatibility/')) {
//         const jobId = path.split('/').pop();
//         loadJobCompatibility(jobId);
//     } else if (path.includes('/manage_jobs')) {
//         // No additional JS needed, handled by Flask
//     }
    
//     // Handle form submissions with validation
//     const forms = document.querySelectorAll('form');
//     forms.forEach(form => {
//         form.addEventListener('submit', validateForm);
//     });
// });

// Fetch current user data
// async function fetchCurrentUser() {
//     try {
//         const response = await fetch('/api/current_user');
//         if (response.ok) {
//             currentUser = await response.json();
//             console.log('Current user loaded:', currentUser);
//         }
//     } catch (error) {
//         console.error('Error fetching current user:', error);
//     }
// }

// Load all jobs
// async function loadAllJobs() {
//     const jobsContainer = document.querySelector('.results-container');
//     if (!jobsContainer) return;
    
//     jobsContainer.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Loading jobs...</p></div>';
    
//     try {
//         const response = await fetch('/api/jobs');
//         if (response.ok) {
//             allJobs = await response.json();
//             displayJobs(allJobs, jobsContainer);
//         } else {
//             jobsContainer.innerHTML = '<div class="error">Failed to load jobs. Please try again later.</div>';
//         }
//     } catch (error) {
//         console.error('Error loading jobs:', error);
//         jobsContainer.innerHTML = '<div class="error">Failed to load jobs. Please try again later.</div>';
//     }
// }

// // Display jobs in container
// function displayJobs(jobs, container) {
//     if (jobs.length === 0) {
//         container.innerHTML = '<p>No jobs found.</p>';
//         return;
//     }
    
//     let html = '<h3>Available Jobs</h3>';
    
//     jobs.forEach(job => {
//         html += `
//             <div class="job-card">
//                 <h3>${job.role_name}</h3>
//                 <p><strong>Company:</strong> ${job.company_name}</p>
//                 <p><strong>Location:</strong> ${job.location || 'Not specified'}</p>
//                 <p><strong>Work Mode:</strong> ${job.work_mode || 'Not specified'}</p>
//                 <p><strong>Weekly Hours:</strong> ${job.weekly_hours || 'Not specified'}</p>
//                 <p><strong>Industry:</strong> ${job.industry.join(', ') || 'Not specified'}</p>
//                 <a href="/job_compatibility/${job.id}" class="btn btn-primary">View Compatibility</a>
//             </div>
//         `;
//     });
    
//     container.innerHTML = html;
// }

// Load job recommendations
// async function loadJobRecommendations() {
//     const recommendationsContainer = document.querySelector('.results-container');
//     if (!recommendationsContainer) return;
    
//     recommendationsContainer.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Analyzing job matches...</p></div>';
    
//     try {
//         const response = await fetch('/api/matches');
//         if (response.ok) {
//             const data = await response.json();
//             displayRecommendations(data.matches, recommendationsContainer);
//         } else {
//             recommendationsContainer.innerHTML = '<div class="error">Failed to load recommendations. Please try again later.</div>';
//         }
//     } catch (error) {
//         console.error('Error loading recommendations:', error);
//         recommendationsContainer.innerHTML = '<div class="error">Failed to load recommendations. Please try again later.</div>';
//     }
// }

// Display job recommendations
// function displayRecommendations(matches, container) {
//     if (matches.length === 0) {
//         container.innerHTML = '<p>No job matches found. Please update your profile to get recommendations.</p>';
//         return;
//     }
    
//     let html = '<h3>Your Job Matches</h3>';
    
//     matches.forEach(match => {
//         const score = Math.round(match.compatibility_score * 100);
        
//         html += `
//             <div class="job-card">
//                 <h3>${match.role_name}</h3>
//                 <p><strong>Company:</strong> ${match.company_name}</p>
//                 <p><strong>Location:</strong> ${match.location || 'Not specified'}</p>
//                 <p><strong>Work Mode:</strong> ${match.work_mode || 'Not specified'}</p>
//                 <p><strong>Compatibility:</strong> <span class="score">${score}%</span></p>
//                 <a href="/job_compatibility/${match.job_id}" class="btn btn-primary">View Details</a>
//             </div>
//         `;
//     });
    
//     container.innerHTML = html;
// }

// Load job compatibility
// async function loadJobCompatibility(jobId) {
//     const compatibilityContainer = document.querySelector('.job-compatibility-container');
//     if (!compatibilityContainer) return;
    
//     compatibilityContainer.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Analyzing compatibility...</p></div>';
    
//     try {
//         const response = await fetch(`/api/compatibility/current/${jobId}`);
//         if (response.ok) {
//             const jobData = await response.json();
//             displayJobCompatibility(jobData, compatibilityContainer);
//         } else {
//             compatibilityContainer.innerHTML = '<div class="error">Failed to load job compatibility. Please try again later.</div>';
//         }
//     } catch (error) {
//         console.error('Error loading job compatibility:', error);
//         compatibilityContainer.innerHTML = '<div class="error">Failed to load job compatibility. Please try again later.</div>';
//     }
// }

// Display job compatibility
// function displayJobCompatibility(jobData, container) {
//     const score = Math.round(jobData.overall_compatibility * 100);
    
//     let html = `
//         <div class="job-card detailed">
//             <h3>${jobData.role_name}</h3>
            
//             <div class="overall-score">
//                 <h4>Overall Compatibility</h4>
//                 <div class="score">${score}%</div>
//             </div>
            
//             <div class="job-details-section">
//                 <h4>Job Details</h4>
//                 <p><strong>Company:</strong> ${jobData.company_name}</p>
//                 <p><strong>Location:</strong> ${jobData.location || 'Not specified'}</p>
//                 <p><strong>Work Mode:</strong> ${jobData.work_mode || 'Not specified'}</p>
//                 <p><strong>Weekly Hours:</strong> ${jobData.weekly_hours || 'Not specified'}</p>
//                 <p><strong>Industry:</strong> ${jobData.industry.join(', ') || 'Not specified'}</p>
//                 <p><strong>Qualifications:</strong> ${jobData.qualifications.join(', ') || 'Not specified'}</p>
//                 <p><strong>Accommodations:</strong> ${jobData.accommodations.join(', ') || 'Not specified'}</p>
//             `;
            
//     // Add application period if available
//     if (jobData.application_period_start || jobData.application_period_end) {
//         html += '<p><strong>Application Period:</strong> ';
//         if (jobData.application_period_start) {
//             html += new Date(jobData.application_period_start).toLocaleDateString();
//         }
//         html += ' to ';
//         if (jobData.application_period_end) {
//             html += new Date(jobData.application_period_end).toLocaleDateString();
//         }
//         html += '</p>';
//     }
    
//     // Add job description if available
//     if (jobData.job_description) {
//         html += `
//             <div class="job-description">
//                 <h4>Job Description</h4>
//                 <p>${jobData.job_description}</p>
//             </div>
//         `;
//     }
// 
//     // Add application materials if available
//     if (jobData.application_materials && jobData.application_materials.length > 0) {
//         html += `
//             <p><strong>Required Application Materials:</strong> ${jobData.application_materials.join(', ')}</p>
//         `;
//     }
    
//     // Add application link if available
//     if (jobData.application_link) {
//         html += `
//             <p><strong>Apply at:</strong> <a href="${jobData.application_link}" target="_blank">${jobData.application_link}</a></p>
//         `;
//     }
    
//     html += `
//             </div>
            
//             <div class="compatibility-factors">
//                 <h4>Compatibility Factors</h4>
//                 <table class="factors-table">
//                     <tr>
//                         <th>Factor</th>
//                         <th>Score</th>
//                     </tr>
//                     <tr>
//                         <td>Location</td>
//                         <td>${Math.round(jobData.factors.location * 100)}%</td>
//                     </tr>
//                     <tr>
//                         <td>Hours</td>
//                         <td>${Math.round(jobData.factors.hours * 100)}%</td>
//                     </tr>
//                     <tr>
//                         <td>Work Mode</td>
//                         <td>${Math.round(jobData.factors.work_mode * 100)}%</td>
//                     </tr>
//                     <tr>
//                         <td>Accommodations</td>
//                         <td>${Math.round(jobData.factors.accommodations * 100)}%</td>
//                     </tr>
//                     <tr>
//                         <td>Qualifications</td>
//                         <td>${Math.round(jobData.factors.qualifications * 100)}%</td>
//                     </tr>
//                 </table>
//             </div>
//         </div>
//     `;
    
//     container.innerHTML = html;
// }

// Form validation
// function validateForm(event) {
//     const form = event.target;
    
//     // Check for required fields
//     const requiredFields = form.querySelectorAll('[required]');
//     let isValid = true;
    
//     requiredFields.forEach(field => {
//         if (!field.value.trim()) {
//             isValid = false;
//             field.classList.add('error-field');
            
//             // Add error message if it doesn't exist
//             let errorMsg = field.parentNode.querySelector('.error-message');
//             if (!errorMsg) {
//                 errorMsg = document.createElement('div');
//                 errorMsg.className = 'error-message';
//                 errorMsg.textContent = 'This field is required';
//                 field.parentNode.appendChild(errorMsg);
//             }
//         } else {
//             field.classList.remove('error-field');
//             const errorMsg = field.parentNode.querySelector('.error-message');
//             if (errorMsg) {
//                 errorMsg.remove();
//             }
//         }
//     });
    
//     // Validate email fields
//     const emailFields = form.querySelectorAll('input[type="email"]');
//     emailFields.forEach(field => {
//         if (field.value && !isValidEmail(field.value)) {
//             isValid = false;
//             field.classList.add('error-field');
            
//             // Add error message if it doesn't exist
//             let errorMsg = field.parentNode.querySelector('.error-message');
//             if (!errorMsg) {
//                 errorMsg = document.createElement('div');
//                 errorMsg.className = 'error-message';
//                 errorMsg.textContent = 'Please enter a valid email address';
//                 field.parentNode.appendChild(errorMsg);
//             }
//         }
//     });
    
//     if (!isValid) {
//         event.preventDefault();
//     }
// }

// Email validation helper
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

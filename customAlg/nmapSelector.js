// Enhanced Problem selection wrapper function
function selectProblem(postData, stringifyOutput = false) {
    let result = null;
    let tsInfo = typeof postData === 'string' ? JSON.parse(postData) : postData;
    console.log('selectProblem: my TSINFO', tsInfo);

    // Get student context
    const studentContext = getStudentContext(tsInfo);
    console.log('Student context:', studentContext);

    // Check for incomplete problems first (existing logic)
    const incompleteProblem = findIncompleteProblem(tsInfo, studentContext);
    if (incompleteProblem) {
        result = {
            problem_name: incompleteProblem.name,
            dynamic_model: tsInfo.dynamic_model
        };
        console.log("selectProblem returning incompleteProblem", result);
    } else {
        // Find next appropriate problem based on multiple criteria
        const candidateProblem = findNextProblem(tsInfo, studentContext);
        
        let previousProblems = tsInfo.dynamic_model?.previousProblems || [];
        let lastProblem = tsInfo.dynamic_model?.lastProblem || {};
        
        if (candidateProblem) {
            previousProblems.push(candidateProblem.name);
            lastProblem[studentContext.device] = candidateProblem.name;
        } else {
            lastProblem[studentContext.device] = "";
        }
        
        result = {
            problem_name: candidateProblem?.name || "",
            dynamic_model: {
                previousProblems: Array.from(new Set(previousProblems)),
                lastProblem: lastProblem,
                // Store additional context for future selections
                studentSkillLevel: studentContext.skillLevel,
                lastAssessment: studentContext.lastAssessment
            }
        };
        console.log('selectProblem returning new problem', result);
    }
    
    return typeof postData === 'string' ? JSON.stringify(result) : result;
}

// Extract student context from available data
function getStudentContext(tsInfo) {
    const device = /android|iphone|ipad|ipod|blackberry|windows phone/i.test(navigator.userAgent) ? "mobile" : "desktop";
    
    return {
        device: device,
        skillLevel: estimateSkillLevel(tsInfo),
        completedProblems: tsInfo.dynamic_model?.previousProblems || [],
        lastAssessment: tsInfo.dynamic_model?.lastAssessment || null,
        preferences: extractStudentPreferences(tsInfo)
    };
}

// Estimate skill level based on completion history and performance
function estimateSkillLevel(tsInfo) {
    const completedProblems = tsInfo.dynamic_model?.previousProblems || [];
    const problems = tsInfo.problems || [];
    
    if (completedProblems.length === 0) return 'beginner';
    
    // Calculate completion rate and difficulty progression
    const completedCount = completedProblems.length;
    const totalProblems = problems.length;
    const completionRate = completedCount / Math.max(totalProblems, 1);
    
    // Check difficulty levels of completed problems
    const completedDifficulties = completedProblems.map(problemName => {
        const problem = problems.find(p => p.name === problemName);
        return parseProblemMetadata(problem?.name || '').difficulty;
    }).filter(d => d);
    
    const avgDifficulty = completedDifficulties.length > 0 
        ? completedDifficulties.reduce((sum, diff) => {
            const diffMap = { 'easy': 1, 'medium': 2, 'hard': 3 };
            return sum + (diffMap[diff] || 1);
        }, 0) / completedDifficulties.length
        : 1;
    
    // Determine skill level
    if (completionRate < 0.3 && avgDifficulty < 1.5) return 'beginner';
    if (completionRate < 0.7 && avgDifficulty < 2.5) return 'intermediate';
    return 'advanced';
}

// Parse problem name for metadata (subnet count, type, difficulty)
function parseProblemMetadata(problemName) {
    if (!problemName) return { subnets: 0, type: 'general', difficulty: 'easy', device: 'desktop' };
    
    // Extract device preference (your existing logic)
    const device = /_\d+$/i.test(problemName) ? "mobile" : "desktop";
    
    // Extract subnet information (assuming naming like "problem_4subnets_easy")
    const subnetMatch = problemName.match(/(\d+)subnet/i);
    const subnets = subnetMatch ? parseInt(subnetMatch[1]) : 0;
    
    // Extract problem type (assuming naming like "routing_problem" or "vlsm_exercise")
    const typeMatch = problemName.match(/^(\w+)_/);
    const type = typeMatch ? typeMatch[1].toLowerCase() : 'general';
    
    // Extract difficulty
    const difficulty = problemName.toLowerCase().includes('hard') ? 'hard' :
                      problemName.toLowerCase().includes('medium') ? 'medium' : 'easy';
    
    return { subnets, type, difficulty, device };
}

// Extract student preferences from their history
function extractStudentPreferences(tsInfo) {
    const completedProblems = tsInfo.dynamic_model?.previousProblems || [];
    const problems = tsInfo.problems || [];
    
    // Analyze completed problems to infer preferences
    const completedMetadata = completedProblems.map(problemName => {
        const problem = problems.find(p => p.name === problemName);
        return parseProblemMetadata(problem?.name || '');
    });
    
    // Find most common problem type
    const typeCounts = {};
    completedMetadata.forEach(meta => {
        typeCounts[meta.type] = (typeCounts[meta.type] || 0) + 1;
    });
    const preferredType = Object.keys(typeCounts).reduce((a, b) => 
        typeCounts[a] > typeCounts[b] ? a : b, 'general');
    
    return {
        preferredType: preferredType,
        maxSubnetsCompleted: Math.max(...completedMetadata.map(m => m.subnets), 0)
    };
}

// Find incomplete problems with context awareness
function findIncompleteProblem(tsInfo, studentContext) {
    return tsInfo.problems?.find(problem => {
        const metadata = parseProblemMetadata(problem.name);
        return problem == (tsInfo.dynamic_model?.lastProblem && tsInfo.dynamic_model.lastProblem[studentContext.device])
            && !/^complete/i.test(problem.completion_status)
            && metadata.device === studentContext.device;
    });
}

// Smart problem selection based on multiple criteria
function findNextProblem(tsInfo, studentContext) {
    const availableProblems = tsInfo.problems.filter(problem => 
        !/^complete/i.test(problem.completion_status) &&
        !studentContext.completedProblems.includes(problem.name)
    );
    
    if (availableProblems.length === 0) return null;
    
    // Score each problem based on student context
    const scoredProblems = availableProblems.map(problem => {
        const metadata = parseProblemMetadata(problem.name);
        let score = 0;
        
        // Device compatibility (high priority)
        if (metadata.device === studentContext.device) score += 100;
        
        // Skill level appropriateness
        const skillScores = {
            'beginner': { 'easy': 50, 'medium': 20, 'hard': 5 },
            'intermediate': { 'easy': 30, 'medium': 50, 'hard': 30 },
            'advanced': { 'easy': 10, 'medium': 30, 'hard': 50 }
        };
        score += skillScores[studentContext.skillLevel]?.[metadata.difficulty] || 20;
        
        // Progressive subnet complexity
        const maxCompleted = studentContext.preferences.maxSubnetsCompleted;
        if (metadata.subnets <= maxCompleted + 2 && metadata.subnets >= maxCompleted) {
            score += 30; // Appropriate progression
        } else if (metadata.subnets > maxCompleted + 2) {
            score -= 20; // Too advanced
        }
        
        // Problem type preference
        if (metadata.type === studentContext.preferences.preferredType) {
            score += 15;
        }
        
        // Variety bonus (encourage trying different types occasionally)
        const recentTypes = studentContext.completedProblems.slice(-3).map(name => {
            const prob = tsInfo.problems.find(p => p.name === name);
            return parseProblemMetadata(prob?.name || '').type;
        });
        if (!recentTypes.includes(metadata.type)) {
            score += 10;
        }
        
        return { problem, score, metadata };
    });
    
    // Sort by score and return best match
    scoredProblems.sort((a, b) => b.score - a.score);
    
    console.log('Problem scores:', scoredProblems.slice(0, 5).map(p => ({
        name: p.problem.name,
        score: p.score,
        metadata: p.metadata
    })));
    
    return scoredProblems[0]?.problem || null;
}

// Utility function to get skill level from external assessment system
// You would integrate this with your actual assessment system
async function fetchSkillLevelFromAssessment(studentId) {
    // Placeholder - replace with actual API call to your assessment system
    // return await assessmentAPI.getSkillLevel(studentId);
    return 'intermediate'; // Default fallback
}

// Helper function for debugging - shows selection reasoning
function explainSelection(tsInfo, selectedProblem) {
    const context = getStudentContext(tsInfo);
    const metadata = parseProblemMetadata(selectedProblem?.name || '');
    
    return {
        studentContext: context,
        selectedProblem: selectedProblem?.name,
        problemMetadata: metadata,
        reasoning: `Selected for ${context.skillLevel} student with ${context.preferences.maxSubnetsCompleted} max subnets completed`
    };
}

module.exports = {
    selectProblem,
    getStudentContext,
    parseProblemMetadata,
    explainSelection
};
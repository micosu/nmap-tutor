// Problem selection wrapper function
function selectProblem(postData, stringifyOutput = false) {

    let result = null;
    let tsInfo = typeof postData === 'string' ? JSON.parse(postData) : postData;
    console.log('selectProblem: my TSINFO', tsInfo);

    const device = /android|iphone|ipad|ipod|blackberry|windows phone/i.test(navigator.userAgent) ? "mobile" : "desktop";
    function wantsDevice(problemName) {
        return /_\d+$/i.test(problemName) ? "mobile" : "desktop";
    }

    const incompleteProblem = tsInfo.problems?.find(
        problem => {                                 // problem.completion_status only on local sequencer
            return problem == (tsInfo.dynamic_model?.lastProblem && tsInfo.dynamic_model.lastProblem[device])
                && !/^complete/i.test(problem.completion_status)
        }
    );
    if(incompleteProblem) {
        result = {
            problem_name: incompleteProblem.name,
            dynamic_model: tsInfo.dynamic_model
        };
        console.log("selectProblem returning incompleteProblem", result);
    } else {
        let candidateProblem = tsInfo.problems.findLast(  // problem.completion_status only on local sequencer
            problem => !/^complete/i.test(problem.completion_status) && wantsDevice(problem.name) == device
        );
    
        let previousProblems = tsInfo.dynamic_model?.previousProblems || [];
        let lastProblem = tsInfo.dynamic_model?.lastProblem || {};
        if(candidateProblem) {
            previousProblems.push(candidateProblem?.name);
            lastProblem[device] = candidateProblem.name;
        } else {
            lastProblem[device] = "";
        }
        result = {
            problem_name: candidateProblem?.name || "",
            dynamic_model: {
                previousProblems: Array.from(new Set(previousProblems)),  // ensures no duplicates
                lastProblem: lastProblem,
            }
        };
        console.log('selectProblem returning new problem', result);
    }
    return typeof postData === 'string' ? JSON.stringify(result) : result;
}

modules.exports = {
    selectProblem,
};

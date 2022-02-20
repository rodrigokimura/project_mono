function getCurriculum() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/cb/api/curricula/${CURRICULUM_ID}/`,
        onSuccess: curriculum => {
            renderCurriculum(curriculum);
            $('body').toast({
                message: 'Curruculum loaded'
            })
        },
    })
}
function renderCurriculum(curriculum) {
    $('input[name=first-name]').val(curriculum.first_name);
    $('input[name=last-name]').val(curriculum.last_name);
    $('textarea[name=bio]').val(curriculum.bio);
    $('input[name=address]').val(curriculum.address);
    renderCompanies(curriculum.companies)
}
function renderCompanies(companies) {
    el = $('#companies');
    el.empty();
    for (company of companies) {
        el.append(`
            <div class="ui fluid card">
                <div class="content">
                    <div class="ui right floated red icon button"><i class="delete icon"></i></div>
                    <div class="ui right floated yellow icon button"><i class="edit icon"></i></div>
                    <div class="header">
                        <i class="building icon"></i>
                        ${company.name}
                    </div>
                    <div class="meta">
                        From to
                    </div>
                </div>
                <div class="extra content">
                    <div class="work-experiences ui cards">
                        ${getWorkExperiencesHTML(company.work_experiences)}
                    </div>
                    <div class="ui basic primary button" style="margin-top: 1em;">Add new work experience</div>
                </div>
            </div>
        `)
    }
}
function getWorkExperiencesHTML(workExperiences) {
    html = '';
    for (workExperience of workExperiences) {
        html += `
            <div class="ui fluid card">
                <div class="content">
                    <div class="ui right floated red icon button"><i class="delete icon"></i></div>
                    <div class="ui right floated yellow icon button"><i class="edit icon"></i></div>
                    <div class="header">
                        <i class="briefcase icon"></i>
                        ${workExperience.job_title}
                    </div>
                    <div class="meta">
                        ${workExperience.description}
                    </div>
                </div>
                <div class="extra content">
                    <span class="right floated">${workExperience.started_at}</span>
                </div>
                <div class="extra content">
                    ${getAcomplishmentsHTML(workExperience.acomplishments)}
                    <div class="ui basic primary button">Add new acomplishment</div>
                </div>
            </div>
        `;
    }
    return html;
}
function getAcomplishmentsHTML(acomplishments) {
    html = '';
    for (acomplishment of acomplishments) {
        html += `
            <div class="ui fluid card">
                <div class="content">
                    <div class="ui right floated red icon button"><i class="delete icon"></i></div>
                    <div class="ui right floated yellow icon button"><i class="edit icon"></i></div>
                    <div class="header">
                        ${acomplishment.title}
                    </div>
                    <div class="meta">
                        ${acomplishment.description}
                    </div>
                </div>
            </div>
        `;
    }
    return html;
}
function saveCurriculum() {
    $.api({
        on: 'now',
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        url: `/cb/api/curricula/${1}/`,
        onSuccess: r => {
            $('body').toast({
                message: CURRICULUM_ID
            })
        },
    })
}
function showCompanyModal(id=undefined) {
    let modal = $('#company-modal');
    if (id === undefined) {
        method = 'POST';
        url = `/cb/api/companies/` 
    } else {
        method = 'PATCH';
        url = `/cb/api/companies/${id}/`;
    }
    modal
        .modal({
            onApprove: () => {
                $.api({
                    on: 'now',
                    method: method,
                    url: url,
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        name: modal.find('input[name=name]').val(),
                        description: modal.find('textarea[name=description]').val(),
                        curriculum: CURRICULUM_ID,
                    },
                    onSuccess: r => {
                        getCurriculum();
                    }
                })
            }
        })
        .modal('show');
}
function addCompany() {
    showCompanyModal();
}
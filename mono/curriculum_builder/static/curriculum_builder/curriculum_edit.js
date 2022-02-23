function stringToDate(dateString) {
    date = dateString.split('-');
    return new Date(date[0], date[1] - 1, date[2]);
}
function dateToString(dateObj) {
    date = new Date(dateObj.toUTCString())
    return date.toISOString().split('T')[0]
}
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
                    <div class="ui right floated red icon button" onclick="deleteCompany(${company.id})"><i class="delete icon"></i></div>
                    <div class="ui right floated yellow icon button" onclick="editCompany(${company.id})"><i class="edit icon"></i></div>
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
                        ${getWorkExperiencesHTML(company.work_experiences, company.id)}
                    </div>
                    <div class="ui basic primary button" style="margin-top: 1em;" onclick="addWorkExperience(${company.id})">
                        Add new work experience
                    </div>
                </div>
            </div>
        `)
    }
}
function getWorkExperiencesHTML(workExperiences, companyId) {
    html = '';
    for (workExperience of workExperiences) {
        html += `
            <div class="ui fluid card">
                <div class="content">
                    <div class="ui right floated red icon button" onclick="deleteWorkExperience(${workExperience.id})"><i class="delete icon"></i></div>
                    <div class="ui right floated yellow icon button" onclick="editWorkExperience(${workExperience.id}, ${companyId})"><i class="edit icon"></i></div>
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
async function loadCompanyToModal(id) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/cb/api/companies/${id}/`,
        onSuccess: company => {
            modal = $('#company-modal');
            modal.find('input[name=name]').val(company.name);
            modal.find('textarea[name=description]').val(company.description);
        },
    })
}
async function showCompanyModal(id) {
    let modal = $('#company-modal');
    if (id === undefined) {
        modal.find('.header').text('Add new company');
        modal.find('input[name=name]').val('');
        modal.find('textarea[name=description]').val('');
        method = 'POST';
        url = `/cb/api/companies/` 
    } else {
        modal.find('.header').text('Edit company');
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
function editCompany(id) {
    loadCompanyToModal(id);
    showCompanyModal(id);
}
function deleteCompany(id) {
    $('body').modal({
        title: 'Confirmation',
        class: 'mini',
        closeIcon: true,
        content: 'Are you sure you want to delete this company?',
        actions: [
            {
                text: 'Cancel',
                class: 'black deny',
            },
            {
                text: 'Yes, delete it',
                class: 'red approve',
            },
        ],
        onApprove: () => {
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/cb/api/companies/${id}/`,
                headers: { 'X-CSRFToken': csrftoken },
                onSuccess: r => {
                    $('body').toast({
                        message: 'Company deleted'
                    });
                    getCurriculum();
                }
            })
        }
    }).modal('show');
}
async function loadWorkExperienceToModal(id) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/cb/api/work_experiences/${id}/`,
        onSuccess: workExperience => {
            modal = $('#work-experience-modal');
            modal.find('input[name=job_title]').val(workExperience.job_title);
            modal.find('textarea[name=description]').val(workExperience.description);
            modal.find('.ui.calendar[data-name=started_at]').calendar('set date', stringToDate(workExperience.started_at));
            modal.find('.ui.calendar[data-name=ended_at]').calendar('set date', stringToDate(workExperience.ended_at));
        },
    })
}
async function showWorkExperienceModal(id, companyId) {
    let modal = $('#work-experience-modal');
    if (id === undefined) {
        modal.find('.header').text('Add new work experience');
        modal.find('input[name=job_title]').val('');
        modal.find('textarea[name=description]').val('');
        modal.find('.ui.calendar[data-name=started_at]').calendar('clear');
        modal.find('.ui.calendar[data-name=ended_at]').calendar('clear');
        method = 'POST';
        url = `/cb/api/work_experiences/` 
    } else {
        modal.find('.header').text('Edit work experience');
        method = 'PATCH';
        url = `/cb/api/work_experiences/${id}/`;
    }
    modal
        .modal({
            onShow: () => {
                modal.find('.ui.calendar[data-name=started_at]').calendar({ type: 'date' });
                modal.find('.ui.calendar[data-name=ended_at]').calendar({ type: 'date' });
            },
            onApprove: () => {
                $.api({
                    on: 'now',
                    method: method,
                    url: url,
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        job_title: modal.find('input[name=job_title]').val(),
                        description: modal.find('textarea[name=description]').val(),
                        started_at: dateToString(modal.find('.ui.calendar[data-name=started_at]').calendar('get date')),
                        ended_at: dateToString(modal.find('.ui.calendar[data-name=ended_at]').calendar('get date')),
                        company: companyId,
                    },
                    onSuccess: r => {
                        getCurriculum();
                    },
                    onFailure: r => {
                        $('body').toast({ title: JSON.stringify(r) })
                    }
                })
            }
        })
        .modal('show');
}
function addWorkExperience(companyId) {
    showWorkExperienceModal(undefined, companyId);
}
function editWorkExperience(id, companyId) {
    loadWorkExperienceToModal(id);
    showWorkExperienceModal(id, companyId);
}
function deleteWorkExperience(id) {
    $('body').modal({
        title: 'Confirmation',
        class: 'mini',
        closeIcon: true,
        content: 'Are you sure you want to delete this work experience?',
        actions: [
            {
                text: 'Cancel',
                class: 'black deny',
            },
            {
                text: 'Yes, delete it',
                class: 'red approve',
            },
        ],
        onApprove: () => {
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/cb/api/work_experiences/${id}/`,
                headers: { 'X-CSRFToken': csrftoken },
                onSuccess: r => {
                    $('body').toast({
                        message: 'Work experience deleted'
                    });
                    getCurriculum();
                }
            })
        }
    }).modal('show');
}
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
        },
    })
}
function renderCurriculum(curriculum) {
    $('input[name=first-name]').val(curriculum.first_name);
    $('input[name=last-name]').val(curriculum.last_name);
    $('textarea[name=bio]').val(curriculum.bio);
    $('input[name=address]').val(curriculum.address);
    renderCompanies(curriculum.companies);
    renderSkills(curriculum.skills);
    renderSocialMediaProfiles(curriculum.social_media_profiles);
}
function renderCompanies(companies) {
    el = $('#companies');
    el.empty();
    for (company of companies) {
        el.append(`
            <div class="ui fluid card">
                <div class="content">
                    <div class="header" style="padding-top: .5em;">
                        <i class="building icon"></i>
                        ${company.name}
                        <div class="ui right floated red icon button" onclick="deleteCompany(${company.id})"><i class="delete icon"></i></div>
                        <div class="ui right floated yellow icon button" onclick="editCompany(${company.id})"><i class="edit icon"></i></div>
                    </div>
                    <div class="meta">
                        From ${company.started_at} to ${company.ended_at}
                    </div>
                </div>
                <div class="extra content">
                    <div class="work-experiences ui cards">
                        ${getWorkExperiencesHTML(company.work_experiences, company.id)}
                    </div>
                    <div class="ui green right labeled icon button" style="margin-top: 1em;" onclick="addWorkExperience(${company.id})">
                        Add new work experience
                        <i class="add icon"></i>
                    </div>
                </div>
            </div>
        `)
    }
}
function renderSkills(skills) {
    el = $('#skills');
    el.empty();
    for (skill of skills) {
        el.append(`
            <div class="ui fluid card">
                <div class="content">
                    <div class="header" style="padding-top: .5em;">
                        <i class="building icon"></i>
                        ${skill.name}
                        <div class="ui right floated red icon button" onclick="deleteSkill(${skill.id})"><i class="delete icon"></i></div>
                        <div class="ui right floated yellow icon button" onclick="editSkill(${skill.id})"><i class="edit icon"></i></div>
                    </div>
                </div>
            </div>
        `)
    }
}
function renderSocialMediaProfiles(socialMediaProfiles) {
    el = $('#social-media-profiles');
    el.empty();
    for (profile of socialMediaProfiles) {
        el.append(`
            <div class="ui fluid card">
                <div class="content">
                    <div class="header" style="padding-top: .5em;">
                        <i class="building icon"></i>
                        ${profile.get_platform_display}
                        <div class="ui right floated red icon button" onclick="deleteSocialMediaProfile(${profile.id})"><i class="delete icon"></i></div>
                        <div class="ui right floated yellow icon button" onclick="editSocialMediaProfile(${profile.id})"><i class="edit icon"></i></div>
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
                    <div class="header" style="padding-top: .5em;">
                        <i class="briefcase icon"></i>
                        ${workExperience.job_title}
                        <div class="ui right floated red icon button" onclick="deleteWorkExperience(${workExperience.id})"><i class="delete icon"></i></div>
                        <div class="ui right floated yellow icon button" onclick="editWorkExperience(${workExperience.id}, ${companyId})"><i class="edit icon"></i></div>
                    </div>
                    <div class="meta">
                        ${workExperience.description}
                    </div>
                </div>
                <div class="extra content">
                    <span class="right floated">${workExperience.started_at}</span>
                </div>
                <div class="extra content">
                    ${getAcomplishmentsHTML(workExperience.acomplishments, workExperience.id)}
                    <div class="ui green right labeled icon button" onclick="addAcomplishment(${workExperience.id})">
                        Add new acomplishment
                        <i class="add icon"></i>
                    </div>
                </div>
            </div>
        `;
    }
    return html;
}
function getAcomplishmentsHTML(acomplishments, workExperienceId) {
    html = '';
    for (acomplishment of acomplishments) {
        html += `
            <div class="ui fluid card">
                <div class="content">
                    <div class="header" style="padding-top: .5em;">
                        ${acomplishment.title}
                        <div class="ui right floated red icon button" onclick="deleteAcomplishment(${acomplishment.id})"><i class="delete icon"></i></div>
                        <div class="ui right floated yellow icon button" onclick="editAcomplishment(${acomplishment.id},${workExperienceId})"><i class="edit icon"></i></div>
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

async function loadResourceToModal(resourceId, url, modalSelector, inputMapping) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `${url}/${resourceId}/`,
        onSuccess: resource => {
            modal = $(modalSelector);
            for ([prop, selector] of Object.entries(inputMapping)) {
                if (selector.includes('dropdown')) { 
                    modal.find(selector).dropdown('set selected', resource[prop]);
                } else if (selector.includes('calendar')) { 
                    modal.find(selector).calendar('set date', stringToDate(resource[prop]));
                } else {
                    modal.find(selector).val(resource[prop]);
                }
            }
        },
    })
}
async function showResourceModal(resourceId, url, modalSelector, resourceType, fkMapping, inputMapping) {
    let modal = $(modalSelector);
    if (resourceId === undefined) {
        modal.find('.header').text(`Add new ${resourceType}`);
        for ([prop, selector] of Object.entries(inputMapping)) {
            if (selector.includes('dropdown')) {
                modal.find(selector).dropdown('clear');
            } else if (selector.includes('calendar')) {
                modal.find(selector).calendar('clear');
            } else {
                modal.find(selector).val('');
            }
        }
        method = 'POST';
        url = `${url}/`
    } else {
        modal.find('.header').text(`Edit ${resourceType}`);
        method = 'PATCH';
        url = `${url}/${resourceId}/`;
    }
    modal
        .modal({
            autofocus: false,
            onShow: () => {
                for ([prop, selector] of Object.entries(inputMapping)) {
                    if (selector.includes('dropdown')) {
                        modal.find(selector).dropdown();
                    } else if (selector.includes('calendar')) {
                        modal.find(selector).calendar({ type: 'date' });
                    }
                }
            },
            onApprove: () => {
                data = {};
                for ([prop, selector] of Object.entries(inputMapping)) {
                    if (selector.includes('dropdown')) {
                        data[prop] = modal.find(selector).dropdown('get value');
                    } else if (selector.includes('calendar')) {
                        data[prop] = dateToString(modal.find(selector).calendar('get date'));
                    } else {
                        data[prop] = modal.find(selector).val();
                    }
                }
                for ([fkName, fkValue] of Object.entries(fkMapping)) {
                    data[fkName] = fkValue;
                }
                $.api({
                    on: 'now',
                    method: method,
                    url: url,
                    headers: { 'X-CSRFToken': csrftoken },
                    data: data,
                    onSuccess: r => {
                        getCurriculum();
                    },
                    onFailure: r => {
                        $('body').toast({ title: JSON.stringify(r) })
                    },
                    onError: r => {
                        $('body').toast({ title: JSON.stringify(r) })
                    }
                })
            }
        })
        .modal('show');
}
async function deleteResource(resourceId, url, resourceType) {
    $('body').modal({
        title: 'Confirmation',
        class: 'mini',
        closeIcon: true,
        content: `Are you sure you want to delete this ${resourceType}?`,
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
                url: `${url}/${resourceId}/`,
                headers: { 'X-CSRFToken': csrftoken },
                onSuccess: r => {
                    $('body').toast({
                        message: `${resourceType} deleted`
                    });
                    getCurriculum();
                }
            })
        }
    }).modal('show');
}

function addCompany() {
    showResourceModal(
        undefined,
        '/cb/api/companies',
        '#company-modal',
        'company',
        {curriculum: CURRICULUM_ID},
        {name: 'input[name=name]', description: 'textarea[name=description]'}
    );
}
function editCompany(id) {
    loadResourceToModal(id, '/cb/api/companies', '#company-modal', {name: 'input[name=name]', description: 'textarea[name=description]'});
    showResourceModal(
        id,
        '/cb/api/companies',
        '#company-modal',
        'company',
        {curriculum: CURRICULUM_ID},
        {name: 'input[name=name]', description: 'textarea[name=description]'}
    );
}
function deleteCompany(id) {
    deleteResource(id, '/cb/api/companies', 'company');
}

function addWorkExperience(companyId) {
    showResourceModal(
        undefined,
        '/cb/api/work_experiences',
        '#work-experience-modal',
        'work experience',
        { company: companyId },
        {
            job_title: 'input[name=job_title]',
            description: 'textarea[name=description]',
            started_at: '.ui.calendar[data-name=started_at]',
            ended_at: '.ui.calendar[data-name=ended_at]',
        }
    );
}
function editWorkExperience(id, companyId) {
    loadResourceToModal(id, '/cb/api/work_experiences', '#work-experience-modal', {
        job_title: 'input[name=job_title]',
        description: 'textarea[name=description]',
        started_at: '.ui.calendar[data-name=started_at]',
        ended_at: '.ui.calendar[data-name=ended_at]',
    })
    showResourceModal(
        id,
        '/cb/api/work_experiences',
        '#work-experience-modal',
        'work experience',
        { company: companyId },
        {
            job_title: 'input[name=job_title]',
            description: 'textarea[name=description]',
            started_at: '.ui.calendar[data-name=started_at]',
            ended_at: '.ui.calendar[data-name=ended_at]',
        }
    );
}
function deleteWorkExperience(id) {
    deleteResource(id, '/cb/api/work_experiences', 'work experience');
}

function addAcomplishment(workExperienceId) {
    showResourceModal(
        undefined,
        '/cb/api/acomplishments',
        '#acomplishment-modal',
        'acomplishment',
        { work_experience: workExperienceId },
        {
            title: 'input[name=title]',
            description: 'textarea[name=description]',
        }
    );
}
function editAcomplishment(id, workExperienceId) {
    loadResourceToModal(id, '/cb/api/acomplishments', '#acomplishment-modal', {
        title: 'input[name=title]',
        description: 'textarea[name=description]',
    });
    showResourceModal(
        id,
        '/cb/api/acomplishments',
        '#acomplishment-modal',
        'acomplishment',
        { work_experience: workExperienceId },
        {
            title: 'input[name=title]',
            description: 'textarea[name=description]',
        }
    );
}
function deleteAcomplishment(id) {
    deleteResource(id, '/cb/api/acomplishments', 'acomplishment');
}

function addSkill() {
    showResourceModal(
        undefined,
        '/cb/api/skills',
        '#skill-modal',
        'skill',
        {curriculum: CURRICULUM_ID},
        {name: 'input[name=name]', description: 'textarea[name=description]'}
    );
}
function editSkill(id) {
    loadResourceToModal(id, '/cb/api/skills', '#skill-modal', {name: 'input[name=name]', description: 'textarea[name=description]'});
    showResourceModal(
        id,
        '/cb/api/skills',
        '#skill-modal',
        'skill',
        {curriculum: CURRICULUM_ID},
        {name: 'input[name=name]', description: 'textarea[name=description]'}
    );
}
function deleteSkill(id) {
    deleteResource(id, '/cb/api/skills', 'skill');
}

function addSocialMediaProfile() {
    showResourceModal(
        undefined,
        '/cb/api/social_media_profiles',
        '#social-media-profile-modal',
        'social media profile',
        {curriculum: CURRICULUM_ID},
        {link: 'input[name=link]', platform: '.ui.dropdown[data-name=platform]'}
    );
}
function editSocialMediaProfile(id) {
    loadResourceToModal(
        id,
        '/cb/api/social_media_profiles',
        '#social-media-profile-modal',
        {link: 'input[name=link]', platform: '.ui.dropdown[data-name=platform]'}
    );
    showResourceModal(
        id,
        '/cb/api/social_media_profiles',
        '#social-media-profile-modal',
        'social media profile',
        {curriculum: CURRICULUM_ID},
        {link: 'input[name=link]', platform: '.ui.dropdown[data-name=platform]'}
    );
}
function deleteSocialMediaProfile(id) {
    deleteResource(id, '/cb/api/social_media_profiles', 'social media profile');
}

import requests
import simplejson as json
from jira.resources import Resource, Issue, Comments, Comment, Project, Attachment, Component, Dashboards, Dashboard, Filter, Votes, Watchers, Worklog, IssueLink, IssueLinkType, IssueType, Priority, Version, Role, Resolution, SecurityLevel, Status, User, CustomFieldOption, RemoteLink

class JIRA(object):

    DEFAULT_OPTIONS = {
        "server": "http://localhost:2990/jira",
        "rest_path": "api",
        "rest_api_version": "2"
    }

    # TODO: add oauth options to constructor
    def __init__(self, options=None, basic_auth=None, oauth=None):
        if options is None:
            options = {}

        self._options = dict(JIRA.DEFAULT_OPTIONS.items() + options.items())

        if basic_auth:
            self._create_http_basic_session(*basic_auth)
        elif oauth:
            self._create_oauth_session(oauth)
        else:
            self._session = requests.session(headers={'content-type': 'application/json'})

### Information about this client

    def client_info(self):
        return self._options['server']

### Universal resource loading

    def find(self, resource_format, ids=None, options=None):
        if options is None:
            options = {}

        resource_options = dict(self._options.items() + options.items())
        resource = Resource(resource_format, resource_options, self._session)
        resource.find(ids)
        return resource

### Application properties

    # non-resource
    def application_properties(self, key=None):
        params = {}
        if key is not None:
            params['key'] = key
        return self._get_json('application-properties', params=params)

    def set_application_property(self, key, value):
        url = self._options['server'] + '/rest/api/2/application-properties/' + key
        payload = {
            'id': key,
            'value': value
        }
        r = self._session.put(url, headers={'content-type': 'application/json'}, data=json.dumps(payload))
        r.raise_for_status()

### Attachments

    def attachment(self, id):
        return self._find_for_resource(Attachment, id)

    # non-resource
    def attachment_meta(self):
        return self._get_json('attachment/meta')

### Components

    def component(self, id):
        return self._find_for_resource(Component, id)

    def create_component(self, **kw):
        pass

    def component_count_related_issues(self, id):
        return self._get_json('component/' + id + '/relatedIssueCounts')['issueCount']

### Custom field options

    def custom_field_option(self, id):
        return self._find_for_resource(CustomFieldOption, id)

### Dashboards

    # TODO: Should this be _get_json instead of resource?
    def dashboards(self, filter=None, startAt=0, maxResults=20):
        dashboards = Dashboards(self._options, self._session)
        params = {}
        if filter is not None:
            params['filter'] = filter
        params['startAt'] = startAt
        params['maxResults'] = maxResults
        dashboards.find(params=params)
        return dashboards

    def dashboard(self, id):
        return self._find_for_resource(Dashboard, id)

### Fields

    # non-resource
    def fields(self):
        return self._get_json('field')

### Filters

    def filter(self, id):
        return self._find_for_resource(Filter, id)

    def favourite_filters(self):
        r_json = self._get_json('filter/favourite')
        filters = [Filter(self._options, self._session, raw_filter_json) for raw_filter_json in r_json]
        return filters

### Groups

    # non-resource
    def groups(self, query=None, exclude=None):
        params = {}
        if query is not None:
            params['query'] = query
        if exclude is not None:
            params['exclude'] = exclude
        return self._get_json('groups/picker', params=params)

### Issues

    def issue(self, id, fields=None, expand=None):
        issue = Issue(self._options, self._session)

        params = {}
        if fields is not None:
            params['fields'] = fields
        if expand is not None:
            params['expand'] = expand
        issue.find(id, params=params)
        return issue

    def create_issue(self, **kw):
        pass

    def createmeta(self, projectKeys=None, projectIds=None, issuetypeIds=None, issuetypeNames=None, expand=None):
        params = {}
        if projectKeys is not None:
            params['projectKeys'] = projectKeys
        if projectIds is not None:
            params['projectIds'] = projectIds
        if issuetypeIds is not None:
            params['issuetypeIds'] = issuetypeIds
        if issuetypeNames is not None:
            params['issuetypeNames'] = issuetypeNames
        if expand is not None:
            params['expand'] = expand
        return self._get_json('issue/createmeta', params)

    # non-resource
    def assign_issue(self, issue, assignee):
        url = self._options['server'] + '/rest/api/2/issue/' + issue + '/assignee'
        payload = {'name': assignee}
        r = self._session.put(url, data=json.dumps(payload))
        r.raise_for_status()

    # TODO: Should this be _get_json instead of resource?
    def comments(self, issue):
        resource = Comments(self._options, self._session)
        resource.find(issue)

        comments = [Comment(self._options, self._session, raw_comment_json) for raw_comment_json in resource.raw['comments']]
        return comments

    def comment(self, issue, comment):
        return self._find_for_resource(Comment, (issue, comment))

    # non-resource
    def editmeta(self, issue):
        return self._get_json('issue/' + issue + '/editmeta')

    def remote_links(self, issue):
        r_json = self._get_json('issue/' + issue + '/remotelink')
        remote_links = [RemoteLink(self._options, self._session, raw_remotelink_json) for raw_remotelink_json in r_json]
        return remote_links

    def remote_link(self, issue, id):
        return self._find_for_resource(RemoteLink, (issue, id))

    # non-resource
    def transitions(self, issue, id=None, expand=None):
        params = {}
        if id is not None:
            params['transitionId'] = id
        if expand is not None:
            params['expand'] = expand
        return self._get_json('issue/' + issue + '/transitions', params)['transitions']

    def votes(self, issue):
        return self._find_for_resource(Votes, issue)

    def watchers(self, issue):
        return self._find_for_resource(Watchers, issue)

    def add_watcher(self, watcher):
        pass

    # also have delete_watcher?

    def worklogs(self, issue):
        r_json = self._get_json('issue/' + issue + '/worklog')
        worklogs = [Worklog(self._options, self._session, raw_worklog_json) for raw_worklog_json in r_json['worklogs']]
        return worklogs

    def worklog(self, issue, id):
        return self._find_for_resource(Worklog, (issue, id))

    def add_worklog(self, issue, **kw):
        pass

    def add_attachment(self, issue, attachment):
        pass

### Issue links

    def create_issue_link(self, **kw):
        pass

    def issue_link(self, id):
        return self._find_for_resource(IssueLink, id)

### Issue link types

    def issue_link_types(self):
        r_json = self._get_json('issueLinkType')
        link_types = [IssueLinkType(self._options, self._session, raw_link_json) for raw_link_json in r_json['issueLinkTypes']]
        return link_types

    def issue_link_type(self, id):
        return self._find_for_resource(IssueLinkType, id)

### Issue types

    def issue_types(self):
        r_json = self._get_json('issuetype')
        issue_types = [IssueType(self._options, self._session, raw_type_json) for raw_type_json in r_json]
        return issue_types

    def issue_type(self, id):
        return self._find_for_resource(IssueType, id)

### User permissions

    # non-resource
    def my_permissions(self, projectKey=None, projectId=None, issueKey=None, issueId=None):
        params = {}
        if projectKey is not None:
            params['projectKey'] = projectKey
        if projectId is not None:
            params['projectId'] = projectId
        if issueKey is not None:
            params['issueKey'] = issueKey
        if issueId is not None:
            params['issueId'] = issueId
        return self._get_json('mypermissions', params=params)

### PrioritiesK

    def priorities(self):
        r_json = self._get_json('priority')
        priorities = [Priority(self._options, self._session, raw_priority_json) for raw_priority_json in r_json]
        return priorities

    def priority(self, id):
        return self._find_for_resource(Priority, id)

### Projects

    def projects(self):
        r_json = self._get_json('project')
        projects = [Project(self._options, self._session, raw_project_json) for raw_project_json in r_json]
        return projects

    def project(self, id):
        return self._find_for_resource(Project, id)

    # non-resource
    def project_avatars(self, project):
        return self._get_json('project/' + project + '/avatars')

    def create_temp_project_avatar(self, project, name, size, avatar_img):
        pass

    def confirm_project_avatar(self, project, **kw):
        pass

    def project_components(self, project):
        r_json = self._get_json('project/' + project + '/components')
        components = [Component(self._options, self._session, raw_comp_json) for raw_comp_json in r_json]
        return components

    def project_versions(self, project):
        r_json = self._get_json('project/' + project + '/versions')
        versions = [Version(self._options, self._session, raw_ver_json) for raw_ver_json in r_json]
        return versions

    # non-resource
    def project_roles(self, project):
        return self._get_json('project/' + project + '/role')

    def project_role(self, project, id):
        return self._find_for_resource(Role, (project, id))

### Resolutions

    def resolutions(self):
        r_json = self._get_json('resolution')
        resolutions = [Resolution(self._options, self._session, raw_res_json) for raw_res_json in r_json]
        return resolutions

    def resolution(self, id):
        return self._find_for_resource(Resolution, id)

### Search

    def search_issues(self, jql_str, startAt=0, maxResults=50, fields=None, expand=None):
        # TODO what to do about the expand, which isn't related to the issues?
        if fields is None:
            fields = []

        search_params = {
            "jql": jql_str,
            "startAt": startAt,
            "maxResults": maxResults,
            "fields": fields,
            "expand": expand
        }

        resource = self._get_json('search', search_params)
        issues = [Issue(self._options, self._session, raw_issue_json) for raw_issue_json in resource['issues']]
        return issues

### Security levels

    def security_level(self, id):
        return self._find_for_resource(SecurityLevel, id)

### Server info

    # non-resource
    def server_info(self):
        return self._get_json('serverInfo')

### Status

    def statuses(self):
        r_json = self._get_json('status')
        statuses = [Status(self._options, self._session, raw_stat_json) for raw_stat_json in r_json]
        return statuses

    def status(self, id):
        return self._find_for_resource(Status, id)

### Users

    def user(self, id, expand=None):
        user = User(self._options, self._session)
        params = {}
        if expand is not None:
            params['expand'] = expand
        user.find(id, params=params)
        return user

    def search_assignable_users_for_projects(self, username, projectKeys, startAt=0, maxResults=50):
        params = {
            'username': username,
            'projectKeys': projectKeys,
            'startAt': startAt,
            'maxResults': maxResults
        }
        r_json = self._get_json('user/assignable/multiProjectSearch', params)
        users = [User(self._options, self._session, raw_user_json) for raw_user_json in r_json]
        return users

    def search_assignable_users_for_issues(self, username, project=None, issueKey=None, expand=None, startAt=0, maxResults=50):
        params = {
            'username': username,
            'startAt': startAt,
            'maxResults': maxResults,
        }
        if project is not None:
            params['project'] = project
        if issueKey is not None:
            params['issueKey'] = issueKey
        if expand is not None:
            params['expand'] = expand
        r_json = self._get_json('user/assignable/search', params)
        users = [User(self._options, self._session, raw_user_json) for raw_user_json in r_json]
        return users

    # non-resource
    def user_avatars(self, username):
        return self._get_json('user/avatars', params={'username': username})

    def create_temp_user_avatar(self, user, filename, size, avatar_img):
        pass

    def confirm_user_avatar(self, user, **kw):
        pass

    def search_users(self, user, startAt=0, maxResults=50):
        params = {
            'username': user,
            'startAt': startAt,
            'maxResults': maxResults
        }
        r_json = self._get_json('user/search', params)
        users = [User(self._options, self._session, raw_user_json) for raw_user_json in r_json]
        return users

    def search_allowed_users_for_issue(self, user, issueKey=None, projectKey=None, startAt=0, maxResults=50):
        params = {
            'username': user,
            'startAt': startAt,
            'maxResults': maxResults,
        }
        if issueKey is not None:
            params['issueKey'] = issueKey
        if projectKey is not None:
            params['projectKey'] = projectKey
        r_json = self._get_json('user/viewissue/search', params)
        users = [User(self._options, self._session, raw_user_json) for raw_user_json in r_json]
        return users

### Versions

    def create_version(self, **kw):
        pass

    def move_version(self, id, **kw):
        pass

    def version(self, id, expand=None):
        version = Version(self._options, self._session)
        params = {}
        if expand is not None:
            params['expand'] = expand
        version.find(id, params=params)
        return version

    def version_count_related_issues(self, id):
        r_json = self._get_json('version/' + id + '/relatedIssueCounts')
        del r_json['self']   # this isn't really an addressable resource
        return r_json

    def version_count_unresolved_issues(self, id):
        return self._get_json('version/' + id + '/unresolvedIssueCount')['issuesUnresolvedCount']

### Session authentication

    def session(self):
        url = '{server}/rest/auth/1/session'.format(**self._options)
        r = self._session.get(url)
        r.raise_for_status()

        user = User(self._options, self._session, json.loads(r.text))
        return user

    def kill_session(self):
        url = self._options['server'] + '/rest/auth/1/session'
        r = self._session.delete(url)
        r.raise_for_status()

### Websudo

    def kill_websudo(self):
        url = self._options['server'] + '/rest/auth/1/websudo'
        r = self._session.delete(url)
        r.raise_for_status()

### Utilities

    def _create_http_basic_session(self, username, password):
        url = self._options['server'] + '/rest/auth/1/session'
        payload = {
            'username': username,
            'password': password
        }

        self._session = requests.session(headers={'content-type': 'application/json'})
        r = self._session.post(url, data=json.dumps(payload))
        r.raise_for_status()

    def _create_oauth_session(self, oauth):
        raise NotImplementedError("oauth support isn't implemented yet")

    def _get_json(self, path, params=None):
        url = '{}/rest/api/2/{}'.format(self._options['server'], path)
        r = self._session.get(url, params=params)
        r.raise_for_status()

        r_json = json.loads(r.text)
        return r_json

    def _find_for_resource(self, resource_cls, ids, expand=None):
        resource = resource_cls(self._options, self._session)
        params = {}
        if expand is not None:
            params['expand'] = expand
        resource.find(ids, params)
        return resource



from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic import TemplateView

# to replace /api/base & /api/owners GeoNode routes with our own:
# unregister old routes before geonode.urls.urlpatterns is imported
from geonode.api.urls import api as geonode_api
geonode_api.unregister('owners')
geonode_api.unregister('base')
from geonode.geoserver.views import layer_acls, resolve_user, layer_batch_download
from geonode.urls import urlpatterns
from maploom.geonode.urls import urlpatterns as maploom_urls
from mapstories.urls import urlpatterns as mapstories_urls
from osgeo_importer.urls import urlpatterns as importer_urlpatterns
from tastypie.api import Api

from mapstory.api.api import MapstoryOwnersResource, InterestsResource
from mapstory.api.resourcebase_api import ResourceBaseResource
from mapstory.api.urls import api as mapstory_api
from mapstory.favorite.urls import api as favorites_api
from mapstory.importers import UploadedLayerResource
from mapstory.views import download_append_csv, download_append_shp
from mapstory.views import GetPageView
from mapstory.views import IndexView
from mapstory.views import LeaderListView
from mapstory.views import layer_detail, layer_create
from mapstory.views import layer_acls_mapstory, resolve_user_mapstory
from mapstory.views import layer_remove, map_remove
from mapstory.views import map_detail
from mapstory.views import new_map
from mapstory.views import ProfileDetail, profile_delete, profile_edit, proxy
from mapstory.views import SearchView
from mapstory.views import get_remote_url


geonode_api.register(ResourceBaseResource())
geonode_api.register(MapstoryOwnersResource())
geonode_api.register(InterestsResource())

importer_api = Api(api_name='importer-api')
# Overwrite Importer URL Routes
importer_api.register(UploadedLayerResource())

# -- Deprecated url routes for Geoserver authentication -- remove after GeoNode 2.1
# -- Use /gs/acls, gs/resolve_user/, gs/download instead
if 'geonode.geoserver' in settings.INSTALLED_APPS:
    geonode_layers_urlpatterns = patterns('',
                           url(r'^layers/acls/?$', layer_acls, name='layer_acls_dep'),
                           url(r'^layers/resolve_user/?$', resolve_user, name='layer_resolve_user_dep'),
                           url(r'^layers/download$', layer_batch_download, name='layer_batch_download_dep'),
                           )

urlpatterns = patterns('',
                       # Home
                       url(r'^$', IndexView.as_view(), name="index_view"),

                       # Adding Threaded Comments app
                       url(r'^articles/comments/', include('django_comments.urls')),

                       # Blog Comments
                       url(r'^blog/comments/', include('fluent_comments.urls')),

                       # Maps
                       url(r'^maps/new/data$', 'mapstory.views.new_map_json', name='new_map_json'),
                       url(r'^maps/(?P<mapid>\d+)/data$', 'mapstory.views.mapstory_map_json', name='mapstory_map_json'),
                       url(r'^maps/new_map', new_map, name='new_map'),
                       url(r'^maps/(?P<storyid>[^/]+)/save$', 'mapstory.views.save_story', name='save_story'),

                       # Story
                       url(r'^story$', 'mapstory.views.new_story_json', name='new_story_json'),
                       url(r'^story/(?P<storyid>[^/]+)/save$', 'mapstory.views.save_story', name='save_story'),
                       url(r'^story/(?P<storyid>[^/]+)/generate_thumbnail', 'mapstory.views.story_generate_thumbnail', name='story_generate_thumbnail'),
                       url(r'^story/(?P<slug>[-\w]+)/$', map_detail, name='mapstory_detail'),
                       url(r'^story/(?P<slug>[-\w]+)/view$', 'mapstory.views.mapstory_view', name='mapstory_view'),
                       url(r'^story/(?P<slug>[-\w]+)/embed$', 'mapstory.views.mapstory_view', name='mapstory_view'),
                       url(r'^story/chapter/new$', 'mapstory.views.new_map_json', name='new_map_json'),

                       # Composer
                       url(r'^story/(?P<slug>[-\w]+)/draft$',
                        'mapstory.views.composer_new_view', {'template': 'composer_new/composer.html'}, name='composer-view'),
                       url(r'^story/new$', new_map, {'template': 'composer_new/composer.html'}, name='new-story'),

                       # Editor
                       url(r'^maps/edit$', new_map, {'template': 'composer/maploom.html'}, name='map-edit'),
                       url(r'^maps/(?P<mapid>\d+)/view$', 'mapstory.views.map_view', {'template': 'composer/maploom.html'}, name='map-view'),

                       # StoryTools
                       url(r'^maps/(?P<mapid>\d+)/viewer$', 'mapstory.views.map_view', {'template': 'viewer/story_viewer.html'}, name='map-viewer'),
                       url(r'^maps/(?P<mapid>\d+)/embed$', 'mapstory.views.map_view', {'template': 'viewer/story_viewer.html'}, name='map-viewer'),

                       url(r"^storyteller/delete/(?P<username>[^/]*)/$", profile_delete, name="profile_delete"),
                       url(r"^storyteller/edit/(?P<username>[^/]*)/$", profile_edit, name="edit_profile"),

                       url(r'^get(?P<slug>\w+)$', GetPageView.as_view(), name='getpage'),
                       url(r'^search/$', SearchView.as_view(), name='search'),
                       url(r'^about/leadership$', LeaderListView.as_view(template_name='mapstory/leaders.html'), name='about-leaders'),
                       url(r'^icons/', include('icon_commons.urls')),
                       url(r'^journal/', include('mapstory.journal.urls')),

                       url(r'^donate$', LeaderListView.as_view(template_name='mapstory/donate.html'), name='donate'),
                       url(r'^proxy/', proxy),
                       url(r'^favorite/', include('mapstory.favorite.urls')),
                       url(r"^flag/", include('mapstory.flag.urls')),

                       # Layers
                       url(r'^layers/acls', layer_acls_mapstory, name='layer_acls_mapstory'),
                       url(r'^layers/create$', layer_create, name='layer_create'),
                       url(r'^layers/download-append-csv$', download_append_csv, name='download_append_csv'),
                       url(r'^layers/download-append-shp$', download_append_shp, name='download_append_shp'),
                       url(r'^layers/resolve_user', resolve_user_mapstory, name='resolve_user_mapstory'),
                       url(r'^layers/(?P<layername>[^/]*)$', layer_detail, name="layer_detail"),
                       url(r'^layers/(?P<layername>[^/]*)/viewer$', layer_detail, {'template': 'viewer/layer_viewer.html'}, name="layer_viewer"),
                       url(r'^layers/(?P<layername>[^/]*)/embed$', layer_detail, {'template': 'viewer/layer_viewer.html'}, name="layer_embed"),
                       url(r'^layers/(?P<layername>[^/]*)/remove$', layer_remove, name="layer_remove"),
                       url(r'^layers/(?P<layername>[^/]*)/remote$', get_remote_url, name="get_remote_url"),

                       url(r'^teams/', include('mapstory.teams.urls', namespace='teams')),
                       url(r'^organizations/', include('mapstory.organizations.urls', namespace='organizations')),
                       url(r'^initiatives/', include('mapstory.initiatives.urls', namespace='initiatives')),
                       url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type="text/plain"), name='robots'),
                       ) + geonode_layers_urlpatterns + urlpatterns

urlpatterns += mapstories_urls

urlpatterns += maploom_urls

urlpatterns += patterns("", url(r'', include(mapstory_api.urls)))

urlpatterns += patterns("", url(r'', include(importer_api.urls)))

urlpatterns += patterns("", url(r'', include(favorites_api.urls)))

urlpatterns += importer_urlpatterns

# this is last to catch reverse lookup from geonode views with the same name
urlpatterns += patterns("",
                        url(r"^storyteller/(?P<slug>[^/]*)/$", ProfileDetail.as_view(), name="profile_detail"),
                        url(r"^storyteller/edit/(?P<username>[^/]*)/$", profile_edit, name="profile_edit"),
                        url(r'^story/(?P<mapid>\d+)/remove$', map_remove, name='map_remove'))


if settings.DEBUG:
    urlpatterns = urlpatterns + patterns('',
        url(r'^testing/(?P<template>.*)$', 'mapstory.views.debug_view'),
    )

if settings.LOCAL_CONTENT:
    urlpatterns = static(settings.STATIC_URL + "assets", document_root=settings.LOCAL_ROOT + "/../../mapstory-assets", show_indexes=True) + urlpatterns

    #urlpatterns += patterns('',
    #    url('', include('social.apps.django_app.urls', namespace='social')),
    #    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    #)

urlpatterns += patterns('',
        url(r'^accounts/', include('allauth.urls')),
)
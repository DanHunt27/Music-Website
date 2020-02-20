from django import forms
from .models import Post, Comment

link_regex_field = forms.RegexField (
    label = "link",
    max_length = 1000,
    regex = r"^https:\/\/soundcloud.com\/[\w-]+\/[\w-]+$",
    error_messages={
        'invalid': ("Must be a link to a song on SoundCloud. Generally looks like: https://soundcloud.com/artist-name/song-name")
    }
)

class PostCreateForm(forms.ModelForm):
    link = link_regex_field

    class Meta:
        model = Post
        fields = ['link', 'artist_name', 'song_name', 'description']

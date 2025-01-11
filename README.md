# Synchronization
A Synchronization software for the Brain Battle Team.

This software aims to streamline the process of synchronizing the EEG data with the 4 POV shots we take of the martial artists.

The app works as a simple video editor, where users can upload the videos, and then click the "Auto-Sync" button to have them synchronize automatically. App also features small individual video editing capabilities such as cutting parts of the videos and adding a time code.

Auto-Sync works by calculating the cross-correlation between the audio extracts of the videos. We choose one video as the base (the longest one in terms of duration), and we compare other videos to this video.

## To-Do
- [ ] Implement synchronization of EEG data with videos.
- [x] Implement synchronization of videos
- [x] Fix bugs regarding the main timeline, where it is impossible to rewind the videos and also impossible to use the timeline after video ends.
- [x] Exporting combined video
- [ ] Better frontend design
- [ ] Documentation


Yours sincerely,
Brain Battle Software Team

# Synchronization
A Synchronization software for the Brain Battle Team.

This software aims to streamline the process of synchronizing the EEG data with the 4 POV shots we take of the martial artists.

The app works as a simple video editor, where users can upload the videos, and then click the "Auto-Sync" button to have them synchronize automatically. App also features small individual video editing capabilities such as cutting parts of the videos and adding a time code.

Auto-Sync works by calculating the cross-correlation between the audio extracts of the videos. We choose one video as the base (the longest one in terms of duration), and we compare other videos to this video.

## Screenshots

Base UI
<img width="1920" height="1051" alt="Synchronization app demo 1" src="https://github.com/user-attachments/assets/3c7d4621-b08a-44de-b184-b0d8a776c46a" />

Before synchronization
<img width="1920" height="1009" alt="Synchronization app demo 2" src="https://github.com/user-attachments/assets/38df7108-411d-4f33-bf14-ea80b3a75529" />

After synchronization
<img width="1918" height="1000" alt="Synchronization app demo 3" src="https://github.com/user-attachments/assets/91443b07-72ac-4257-b218-91013af13811" />



## To-Do
- [ ] Implement synchronization of EEG data with videos.
- [x] Implement synchronization of videos
- [x] Fix bugs regarding the main timeline, where it is impossible to rewind the videos and also impossible to use the timeline after video ends.
- [x] Exporting combined video
- [ ] Better frontend design
- [ ] Documentation


Yours sincerely,
Brain Battle Software Team

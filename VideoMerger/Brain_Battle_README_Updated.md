Brain Battle
Video Merger Module: By Yasin Gasimov and Aryan Panicker

The following paper describes the collaborative development of the Video Merger module for Brain Battle, one element in the project undertaken by Aryan Panicker and Yasin Gasimov. This Python tool has been developed to let users easily merge multiple videos into a single file. We used the MoviePy library a decision we had to make after looking at many other alternatives.
Timeline of Development: A Month-by-Month Breakdown
Our development process spanned several months, each phase focusing on specific features and improvements:
October: Initial Exploration with FFMPEG
Hours Worked: Yasin: 17 hours, Aryan: 16 hours
Initially, we explored the capabilities of FFMPEG, a powerful multimedia framework. However, we encountered significant challenges related to configuration complexity and cryptic error messages. These hurdles hampered our progress and led us to seek a more manageable alternative. This phase was crucial in understanding the underlying processes involved in video manipulation and informed our subsequent decision to switch to MoviePy.
November: Transition to MoviePy and Core Functionality
Hours Worked: Yasin: 14 hours, Aryan: 14 hours
Recognizing the need for a more user-friendly and reliable solution, we transitioned to MoviePy. This library provided a streamlined interface and simplified the video processing workflow. During this phase, we collaboratively designed and implemented the core functionality for merging media files. This involved understanding MoviePy's API, implementing video concatenation, and basic error handling.
Late November: Refactoring into a Reusable Library
Hours Worked: Yasin: 19 hours, Aryan: 21 hours
To enhance the module's reusability and maintainability, we refactored the code into a self-contained library. This involved abstracting the merging logic into separate functions and classes. We also dedicated significant time to rigorous testing and debugging to ensure the library's stability and reliability. This phase significantly improved the codebase's structure and laid the foundation for future enhancements.
December: Implementing the Timestamp Feature
Hours Worked: Yasin: 23 hours, Aryan: 26 hours
A key feature added during this period was the timestamp option for exported videos. Yasin focused on designing the underlying implementation for timestamp generation and integration with the video merging process. Aryan concentrated on refining the user interface to accommodate this new feature and diligently addressed edge cases to ensure consistent performance across various scenarios.
Expanding Functionality: Key Enhancements
Beyond the core features, we implemented several significant enhancements to improve the user experience and expand the module's capabilities:
In-app Tutorial: Providing User Guidance
Hours Worked: Yasin: 9 hours, Aryan: 9 hours
To facilitate user onboarding and provide easy access to help resources, we implemented an in-app tutorial. This feature includes a help icon within the application's interface. Clicking this icon triggers a pop-up screen containing multiple pages of detailed instructions and explanations covering all functionalities of the application. Yasin designed the UI layout for the tutorial screen and implemented the help button functionality. Aryan then connected the button to the tutorial content and thoroughly tested the interface to ensure its usability and responsiveness.
Further Automizing the Process: Streamlining Workflows
Hours Worked: Yasin: 25 hours, Aryan: 23 hours
Recognizing the need to minimize manual intervention, we developed an auto-processing functionality. This feature allows users to automate the video merging process based on a pre-defined folder structure. Users can create a main folder containing subfolders, each representing a distinct set of videos and associated data (e.g., CSV files). The application then iterates through each subfolder, automatically applying the merging and data integration functions. This feature significantly reduces the time and effort required to process large numbers of videos. 
Yasin focused on the core logic for handling the folder structures (17 hours) and refined the auto-processing functionality (8 hours).
Aryan implemented a progress bar to provide users with real-time feedback on the processing status (16 hours) and also dedicated time to optimizing the video merging process itself (7 hours).
Progress Bar and Enhanced Video Merging:
Hours Worked: Yasin: 13 hours, Aryan: 11 hours
To further enhance the user experience during automated processing, we implemented a progress bar. This visual indicator provides users with real-time feedback on the progress of the merging process, including status updates (e.g., which file is currently being processed). This improvement provides transparency and allows users to monitor the application's progress. Yasin focused on debugging and testing the progress bar's functionality to ensure its accuracy and responsiveness, while Aryan focused on further refining the video merging algorithms for improved performance and stability.
Total Work Hours:
Yasin Gasimov: 120 hours
Aryan Panicker: 120 hours
Conclusion: A Foundation for Future Development
The Video Merger module represents a significant accomplishment, showcasing our collaborative efforts and technical skills. The project emphasized best practices in software development, including modular design, robust error handling, and effective utilization of external libraries. With a combined effort of 240 hours, we have established a robust foundation for future enhancements. Potential future improvements include expanding support for additional video formats, implementing advanced editing features, and developing a more intuitive graphical user interface. This project has not only equipped us with valuable experience but has also laid the groundwork for further innovation in video processing technology.


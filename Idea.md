# Project: S-Eye - Driver Safety Warning and Monitoring System

## 1. General Information
* [cite_start]**Institution:** Vietnam-Korea University of Information and Communication Technology (VKU) [cite: 1]
* [cite_start]**Department:** Computer Science [cite: 1]
* [cite_start]**Team Members:** * Trần Ka Bun (MSV: 23IT.B015 - Class: 23SE4) [cite: 4]
    * [cite_start]Nguyễn Phan Nhật Quang (MSV: 23IT.B176 - Class: 23SE4) [cite: 4]
* **Instructor:** TS. [cite_start]Lý Quỳnh Trân [cite: 4]

## 2. Project Description
[cite_start]**S-Eye** is a desktop application designed to monitor driver status via a camera[cite: 8]. [cite_start]The system continuously scans the face and uses image processing algorithms to analyze eye openness[cite: 9]. 

[cite_start]If the driver closes their eyes beyond a specified time or shows signs of drowsiness, the app triggers an audio alarm and visual notification[cite: 10].

## 3. Technical Objectives
* [cite_start]**Manual Implementation:** Do not use pre-packaged AI libraries; implement algorithms manually to understand pixel-level processing[cite: 13, 17].
* [cite_start]**Optimization:** Ensure the system runs efficiently on medium-spec computers[cite: 13].
* [cite_start]**Accuracy:** Target an accuracy rate of over 80%[cite: 17].

## 4. Technical Stack & Approach
* [cite_start]**Language:** Python[cite: 14].
* [cite_start]**Key Algorithm:** Eye Aspect Ratio (EAR) based on facial landmarks[cite: 15].
* [cite_start]**Mathematical Core:** Euclidean distance calculation between eye landmarks[cite: 23].
* [cite_start]**Processing Pipeline:** 1.  Image preprocessing (Grayscale conversion, noise filtering)[cite: 21].
    2.  [cite_start]Face and region-of-interest (ROI) detection[cite: 22].
    3.  [cite_start]EAR calculation and logic thresholding for drowsiness vs. normal blinking[cite: 24].


## 5. Implementation Phases
1.  [cite_start]**Research:** Study EAR/HOG algorithms and collect eye datasets[cite: 30].
2.  [cite_start]**Preprocessing:** Build modules for image filtering and face detection[cite: 30].
3.  [cite_start]**Core Logic:** Implement EAR math and warning logic[cite: 30].
4.  [cite_start]**UI/UX:** Develop the monitoring interface and integrate audio alerts[cite: 30].
5.  [cite_start]**Testing:** Evaluate accuracy across different lighting conditions and angles[cite: 27, 30].

## 6. Execution Plan (2026)
| Week | Timeframe | Tasks |
| :--- | :--- | :--- |
| 1 | 18/03 – 25/03 | [cite_start]Research EAR/HOG, data collection [cite: 30] |
| 2 | 26/03 - 05/04 | [cite_start]Preprocessing and face detection modules [cite: 30] |
| 3 | 06/04 - 20/04 | [cite_start]EAR algorithm and drowsiness logic [cite: 30] |
| 4 | 21/04 - 05/05 | [cite_start]UI development and audio integration [cite: 30] |
| 5 | 06/05 – 14/05 | [cite_start]Testing, tuning, and final report [cite: 30] |
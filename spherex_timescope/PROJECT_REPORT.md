# SPHEREx TimeScope — Project Report

## 1. Overview
SPHEREx TimeScope is an educational web application designed to make public SPHEREx infrared spectral-image data easier to explore. It provides a simple interface for browsing the public archive and comparing selected observations.

## 2. Problem
Scientific mission archives contain large numbers of files organized by release, observing period, processing version, and detector. New users may find it difficult to locate, inspect, and visually compare these data products.

## 3. Proposed solution
The application provides a guided browser for public SPHEREx Level 2 data. Users can navigate archive folders, inspect available FITS files, load selected observations, view image previews, and compare metadata and image appearance.

## 4. Main features
1. **Archive Explorer:** browse QR2 and QR3 Level 2 data in public AWS S3.
2. **FITS File Browser:** list files by planning period, processing version, and detector.
3. **Image Viewer:** display selected FITS image extensions.
4. **Observation Metadata:** display observation time, coordinates, object, observation ID, band/detector, and image dimensions when recorded in the selected header.
5. **Visual Comparison:** display two selected images side by side and an exploratory pixel-difference preview when array dimensions match.

## 5. Technology
- Python
- Streamlit
- Astropy
- NumPy
- Matplotlib
- Pandas
- Boto3 / Amazon S3 anonymous access

## 6. Data
The application uses public SPHEREx Quick Release Level 2 data hosted by Caltech/IPAC IRSA in the `nasa-irsa-spherex` AWS S3 bucket. QR3 data DOI: 10.26131/IRSA662.

## 7. Workflow
1. User chooses QR2 or QR3.
2. Application lists available planning-period folders.
3. User chooses a processing version and detector.
4. Application lists FITS files in that folder.
5. User selects two files.
6. Application downloads the selected files, reads their FITS image extensions and headers, and displays previews and metadata.
7. The app reports whether recognized observation-time metadata differ.

## 8. Limitations and future work
This MVP does not automatically search the entire archive by celestial coordinates. It does not yet verify that two selected images cover the same sky footprint or wavelength interval. The pixel-difference display is exploratory only; it is not WCS-registered or photometrically calibrated.

Future improvements:
- Coordinate-based observation discovery using SIA2/TAP when those services are available.
- WCS-based sky-footprint matching and image reprojection.
- Wavelength-solution matching and quality-flag masking.
- Scientifically calibrated temporal difference analysis.
- Exportable comparison reports and a map/sky-position interface.

## 9. Conclusion
SPHEREx TimeScope provides a practical starting point for exploring real SPHEREx Level 2 data through a simple interface. It lowers the barrier to archive navigation and visual inspection while clearly communicating the additional checks required for scientific time-domain analysis.

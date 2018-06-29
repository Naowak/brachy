import dicom_parser
from matplotlib import pyplot as plt 

dip = dicom_parser.DicomParser("../tests/data_tests/prostate")
density = dip.get_DICOM_densite(91)
hounsfield = dip.get_DICOM_hounsfield(91)
ROI = dip.get_DICOM_ROI(3)
contourage = dip.get_DICOM_contourage(3, 91)
maillage = dip.get_DICOM_maillage()

print(maillage)

# plt.imshow(hounsfield)
# plt.show()
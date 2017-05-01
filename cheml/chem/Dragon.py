import pandas as pd
import numpy as np
from lxml import objectify, etree
import subprocess
import warnings
import os 
from ..utils.utilities import std_datetime_str


def _bool_formatter(bool):
    if bool:
        return("true")
    else:
        return("false")


class Dragon(object):
    """
    An interface to Dragon 6 and 7 software.

    :param: version: int, optional (default=7)
        The version of available Dragon on the user's machine. (available versions 6 or 7)
    
    :param: Weights: list, optional (default=["Mass","VdWVolume","Electronegativity","Polarizability","Ionization","I-State"])
        A list of weights to be used

    :param: blocks: list, optional (default=False)
        A list of descriptor blocks' id. For all of them parameter SelectAll="true" is given. 
        To select descriptors one by one based on descriptor names, use Script Wizard in Drgon GUI.
                
    :param: external: boolean, optional (default=False)
        If True, include external variables at the end of each saved file.

    :return: Dragon Script and descriptors.
    """
    def __init__(self, version = 6,CheckUpdates = True,SaveLayout = True, PreserveTemporaryProjects = True,
                ShowWorksheet = False,Decimal_Separator = ".",Missing_String = "NaN",
                DefaultMolFormat = "1",HelpBrowser = "/usr/bin/xdg-open",RejectUnusualValence = False,
                Add2DHydrogens = False,MaxSRforAllCircuit = "19",MaxSR = "35",
                MaxSRDetour = "30",MaxAtomWalkPath = "2000",LogPathWalk = True,
                LogEdge = True,Weights = ["Mass","VdWVolume","Electronegativity","Polarizability","Ionization","I-State"],
                SaveOnlyData = False,SaveLabelsOnSeparateFile = False,SaveFormatBlock = "%b-%n.txt",
                SaveFormatSubBlock = "%b-%s-%n-%m.txt",SaveExcludeMisVal = False,SaveExcludeAllMisVal = False,
                SaveExcludeConst = False,SaveExcludeNearConst = False,SaveExcludeStdDev = False,
                SaveStdDevThreshold = "0.0001",SaveExcludeCorrelated = False,SaveCorrThreshold = "0.95",
                SaveExclusionOptionsToVariables = False,SaveExcludeMisMolecules = False,
                SaveExcludeRejectedMolecules = False,blocks = range(1,30),molInput = "stdin",
                molInputFormat = "SMILES",molFile = None,SaveStdOut = False,SaveProject = False,
                SaveProjectFile = "Dragon_project.drp",SaveFile = True,SaveType = "singlefile",
                SaveFilePath = "Dragon_descriptors.txt",logMode = "file",logFile = "Dragon_log.txt",
                external = False,fileName = None,delimiter = ",",consecutiveDelimiter = False,MissingValue = "NaN",
                RejectDisconnectedStrucuture = False, RetainBiggestFragment = False, DisconnectedCalculationOption = "0",
                RoundCoordinates = True, RoundWeights = True, RoundDescriptorValues = True, knimemode = False):
        self.version = version
        self.CheckUpdates = CheckUpdates
        self.PreserveTemporaryProjects = PreserveTemporaryProjects
        self.SaveLayout = SaveLayout
        self.ShowWorksheet = ShowWorksheet
        self.Decimal_Separator = Decimal_Separator
        self.Missing_String = Missing_String
        self.DefaultMolFormat = DefaultMolFormat
        self.HelpBrowser = HelpBrowser
        self.RejectUnusualValence = RejectUnusualValence
        self.Add2DHydrogens = Add2DHydrogens
        self.MaxSRforAllCircuit = MaxSRforAllCircuit
        self.MaxSR = MaxSR
        self.MaxSRDetour = MaxSRDetour
        self.MaxAtomWalkPath = MaxAtomWalkPath
        self.LogPathWalk = LogPathWalk
        self.LogEdge = LogEdge
        self.Weights = Weights
        self.SaveOnlyData = SaveOnlyData
        self.SaveLabelsOnSeparateFile = SaveLabelsOnSeparateFile
        self.SaveFormatBlock = SaveFormatBlock
        self.SaveFormatSubBlock = SaveFormatSubBlock
        self.SaveExcludeMisVal = SaveExcludeMisVal
        self.SaveExcludeAllMisVal = SaveExcludeAllMisVal
        self.SaveExcludeConst = SaveExcludeConst
        self.SaveExcludeNearConst = SaveExcludeNearConst
        self.SaveExcludeStdDev = SaveExcludeStdDev
        self.SaveStdDevThreshold = SaveStdDevThreshold
        self.SaveExcludeCorrelated = SaveExcludeCorrelated
        self.SaveCorrThreshold = SaveCorrThreshold
        self.SaveExclusionOptionsToVariables = SaveExclusionOptionsToVariables
        self.SaveExcludeMisMolecules = SaveExcludeMisMolecules
        self.SaveExcludeRejectedMolecules = SaveExcludeRejectedMolecules
        self.blocks = blocks
        self.molInput = molInput
        self.molInputFormat = molInputFormat
        self.molFile = molFile
        self.SaveStdOut = SaveStdOut
        self.SaveProject = SaveProject
        self.SaveProjectFile = SaveProjectFile
        self.SaveFile = SaveFile
        self.SaveType = SaveType
        self.SaveFilePath = SaveFilePath
        self.logMode = logMode
        self.logFile = logFile
        self.external = external
        self.fileName = fileName
        self.delimiter = delimiter
        self.consecutiveDelimiter = consecutiveDelimiter
        self.MissingValue = MissingValue

        self.RejectDisconnectedStrucuture = RejectDisconnectedStrucuture
        self.RetainBiggestFragment = RetainBiggestFragment
        self.DisconnectedCalculationOption = DisconnectedCalculationOption
        self.RoundCoordinates = RoundCoordinates
        self.RoundWeights = RoundWeights
        self.RoundDescriptorValues = RoundDescriptorValues
        self.knimemode = knimemode
    
    def script_wizard(self, script='new', output_directory='./'):
        """
        The script_wizard is designed to build a Dragon script file. The name and
        the functionality of this function is the same as available Script wizard 
        in the Dragon Graphic User Interface.
        Note: All reported nodes are mandatory, except the <EXTERNAL> tag
        Note: Script for version 7 doesn't support fingerprints block

        :param: script: string, optional (default="new")
            If "new" start with a new script. If you want to load an existing script,
            pass the filename with drs format.

        :param: output_directory: string, optional (default = './')
            the path to the working directory to store output files.

        :: dragon: xml element
            Dragon script in  xml format.
        
        :: drs: string
            Dragon script file name
        
        :: data_path: string
            The path+name of saved data file in any format. If saveType is 'block' 
            or 'subblock' data_path is just the path to the directory that all data 
            files have been saved. 
             
        :return: class parameters
        """
        if output_directory[-1] == '/':
            self.output_directory = output_directory
        else:
            self.output_directory = output_directory + '/'
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        if script == 'new':
            if self.version == 6:
                self.dragon = objectify.Element("DRAGON", version="%i.0.0"%self.version,  script_version="1", generation_date=std_datetime_str('date').replace('-','/'))

                OPTIONS = objectify.SubElement(self.dragon, "OPTIONS")
                OPTIONS.append(objectify.Element("CheckUpdates", value = _bool_formatter(self.CheckUpdates)))
                OPTIONS.append(objectify.Element("SaveLayout", value = _bool_formatter(self.SaveLayout)))
                OPTIONS.append(objectify.Element("ShowWorksheet", value = _bool_formatter(self.ShowWorksheet)))
                OPTIONS.append(objectify.Element("Decimal_Separator", value = self.Decimal_Separator))
                OPTIONS.append(objectify.Element("Missing_String", value = self.Missing_String))
                OPTIONS.append(objectify.Element("DefaultMolFormat", value = self.DefaultMolFormat))
                OPTIONS.append(objectify.Element("HelpBrowser", value = self.HelpBrowser))
                OPTIONS.append(objectify.Element("RejectUnusualValence", value = _bool_formatter(self.RejectUnusualValence)))
                OPTIONS.append(objectify.Element("Add2DHydrogens", value = _bool_formatter(self.Add2DHydrogens)))
                OPTIONS.append(objectify.Element("MaxSRforAllCircuit", value = self.MaxSRforAllCircuit))
                OPTIONS.append(objectify.Element("MaxSR", value = self.MaxSR))
                OPTIONS.append(objectify.Element("MaxSRDetour", value = self.MaxSRDetour))
                OPTIONS.append(objectify.Element("MaxAtomWalkPath", value = self.MaxAtomWalkPath))
                OPTIONS.append(objectify.Element("LogPathWalk", value = _bool_formatter(self.LogPathWalk)))
                OPTIONS.append(objectify.Element("LogEdge", value = _bool_formatter(self.LogEdge)))
                Weights = objectify.SubElement(OPTIONS, "Weights")
                for weight in self.Weights:
                    if weight not in ["Mass","VdWVolume","Electronegativity","Polarizability","Ionization","I-State"]:
                        msg = "'%s' is not a valid weight type."%weight 
                        raise ValueError(msg)
                    Weights.append(objectify.Element('weight', name = weight))
                OPTIONS.append(objectify.Element("SaveOnlyData", value = _bool_formatter(self.SaveOnlyData)))
                OPTIONS.append(objectify.Element("SaveLabelsOnSeparateFile", value = _bool_formatter(self.SaveLabelsOnSeparateFile)))
                OPTIONS.append(objectify.Element("SaveFormatBlock", value = self.SaveFormatBlock))
                OPTIONS.append(objectify.Element("SaveFormatSubBlock", value = self.SaveFormatSubBlock))
                OPTIONS.append(objectify.Element("SaveExcludeMisVal", value = _bool_formatter(self.SaveExcludeMisVal)))
                OPTIONS.append(objectify.Element("SaveExcludeAllMisVal", value = _bool_formatter(self.SaveExcludeAllMisVal)))
                OPTIONS.append(objectify.Element("SaveExcludeConst", value = _bool_formatter(self.SaveExcludeConst)))
                OPTIONS.append(objectify.Element("SaveExcludeNearConst", value = _bool_formatter(self.SaveExcludeNearConst)))
                OPTIONS.append(objectify.Element("SaveExcludeStdDev", value = _bool_formatter(self.SaveExcludeStdDev)))
                OPTIONS.append(objectify.Element("SaveStdDevThreshold", value = self.SaveStdDevThreshold))
                OPTIONS.append(objectify.Element("SaveExcludeCorrelated", value = _bool_formatter(self.SaveExcludeCorrelated)))
                OPTIONS.append(objectify.Element("SaveCorrThreshold", value = self.SaveCorrThreshold))
                OPTIONS.append(objectify.Element("SaveExclusionOptionsToVariables", value = _bool_formatter(self.SaveExclusionOptionsToVariables)))
                OPTIONS.append(objectify.Element("SaveExcludeMisMolecules", value = _bool_formatter(self.SaveExcludeMisMolecules)))
                OPTIONS.append(objectify.Element("SaveExcludeRejectedMolecules", value = _bool_formatter(self.SaveExcludeRejectedMolecules)))
         
                DESCRIPTORS = objectify.SubElement(self.dragon, "DESCRIPTORS")
                for i in self.blocks:
                    if i<1 or i>29:
                        msg = "block id must be in range 1 to 29."
                        raise ValueError(msg)
                    DESCRIPTORS.append(objectify.Element('block', id = "%i"%i, SelectAll = "true"))
        
                MOLFILES = objectify.SubElement(self.dragon, "MOLFILES")
                MOLFILES.append(objectify.Element("molInput", value = self.molInput))
                if self.molInput == "stdin":
                    if self.molInputFormat not in ['SYBYL','MDL','HYPERCHEM','SMILES','MACROMODEL']:
                        msg = "'%s' is not a valid molInputFormat. Formats:['SYBYL','MDL','HYPERCHEM','SMILES','MACROMODEL']"%self.molInputFormat
                        raise ValueError(msg) 
                    MOLFILES.append(objectify.Element("molInputFormat", value = self.molInputFormat)) 
                elif self.molInput == "file":
                    MOLFILES.append(objectify.Element("molFile", value = self.molFile)) 
                else:
                    msg = "Enter a valid molInput: 'stdin' or 'file'"
                    raise ValueError(msg)
                OUTPUT = objectify.SubElement(self.dragon, "OUTPUT")
                OUTPUT.append(objectify.Element("SaveStdOut", value = _bool_formatter(self.SaveStdOut)))
                OUTPUT.append(objectify.Element("SaveProject", value = _bool_formatter(self.SaveProject)))
                if self.SaveProject:
                    OUTPUT.append(objectify.Element("SaveProjectFile", value = self.SaveProjectFile))
                OUTPUT.append(objectify.Element("SaveFile", value = _bool_formatter(self.SaveFile)))
                if self.SaveFile:
                    OUTPUT.append(objectify.Element("SaveType", value = self.SaveType)) # value = "[singlefile/block/subblock]"
                    OUTPUT.append(objectify.Element("SaveFilePath", value = self.output_directory+self.SaveFilePath)) #Specifies the file name for saving results as a plan text file(s), if the "singlefile" option is set; if "block" or "subblock" are set, specifies the path in which results files will be saved.
                OUTPUT.append(objectify.Element("logMode", value = self.logMode)) # value = [none/stderr/file]
                if self.logMode == "file":
                    OUTPUT.append(objectify.Element("logFile", value = self.output_directory+self.logFile))
            
                if self.external:
                    EXTERNAL = objectify.SubElement(self.dragon, "EXTERNAL") 
                    EXTERNAL.append(objectify.Element("fileName", value = self.fileName))
                    EXTERNAL.append(objectify.Element("delimiter", value = self.delimiter))
                    EXTERNAL.append(objectify.Element("consecutiveDelimiter", value = _bool_formatter(self.consecutiveDelimiter)))
                    EXTERNAL.append(objectify.Element("MissingValue", value = self.MissingValue))
                self._save_script()
            
            elif self.version == 7:
                self.dragon = objectify.Element("DRAGON", version="%i.0.0"%self.version, description="Dragon7 - FP1 - MD5270", script_version="1", generation_date=std_datetime_str('date').replace('-','/'))

                OPTIONS = objectify.SubElement(self.dragon, "OPTIONS")
                OPTIONS.append(objectify.Element("CheckUpdates", value = _bool_formatter(self.CheckUpdates)))
                OPTIONS.append(objectify.Element("PreserveTemporaryProjects", value = _bool_formatter(self.PreserveTemporaryProjects)))
                OPTIONS.append(objectify.Element("SaveLayout", value = _bool_formatter(self.SaveLayout)))
#                 OPTIONS.append(objectify.Element("ShowWorksheet", value = _bool_formatter(self.ShowWorksheet)))
                OPTIONS.append(objectify.Element("Decimal_Separator", value = self.Decimal_Separator))
                if self.Missing_String == "NaN": self.Missing_String = "na"
                OPTIONS.append(objectify.Element("Missing_String", value = self.Missing_String))
                OPTIONS.append(objectify.Element("DefaultMolFormat", value = self.DefaultMolFormat))
#                 OPTIONS.append(objectify.Element("HelpBrowser", value = self.HelpBrowser))
                OPTIONS.append(objectify.Element("RejectDisconnectedStrucuture", value = _bool_formatter(self.RejectDisconnectedStrucuture)))
                OPTIONS.append(objectify.Element("RetainBiggestFragment", value = _bool_formatter(self.RetainBiggestFragment)))
                OPTIONS.append(objectify.Element("RejectUnusualValence", value = _bool_formatter(self.RejectUnusualValence)))
                OPTIONS.append(objectify.Element("Add2DHydrogens", value = _bool_formatter(self.Add2DHydrogens)))
                OPTIONS.append(objectify.Element("DisconnectedCalculationOption", value = self.DisconnectedCalculationOption))
                OPTIONS.append(objectify.Element("MaxSRforAllCircuit", value = self.MaxSRforAllCircuit))
#                 OPTIONS.appendm(objectify.Element("MaxSR", value = self.MaxSR))
                OPTIONS.append(objectify.Element("MaxSRDetour", value = self.MaxSRDetour))
                OPTIONS.append(objectify.Element("MaxAtomWalkPath", value = self.MaxAtomWalkPath))
                OPTIONS.append(objectify.Element("RoundCoordinates", value = _bool_formatter(self.RoundCoordinates)))
                OPTIONS.append(objectify.Element("RoundWeights", value = _bool_formatter(self.RoundWeights)))
                OPTIONS.append(objectify.Element("LogPathWalk", value = _bool_formatter(self.LogPathWalk)))
                OPTIONS.append(objectify.Element("LogEdge", value = _bool_formatter(self.LogEdge)))
                Weights = objectify.SubElement(OPTIONS, "Weights")
                for weight in self.Weights:
                    if weight not in ["Mass","VdWVolume","Electronegativity","Polarizability","Ionization","I-State"]:
                        msg = "'%s' is not a valid weight type."%weight 
                        raise ValueError(msg)
                    Weights.append(objectify.Element('weight', name = weight))
                OPTIONS.append(objectify.Element("SaveOnlyData", value = _bool_formatter(self.SaveOnlyData)))
                OPTIONS.append(objectify.Element("SaveLabelsOnSeparateFile", value = _bool_formatter(self.SaveLabelsOnSeparateFile)))
                OPTIONS.append(objectify.Element("SaveFormatBlock", value = self.SaveFormatBlock))
                OPTIONS.append(objectify.Element("SaveFormatSubBlock", value = self.SaveFormatSubBlock))
                OPTIONS.append(objectify.Element("SaveExcludeMisVal", value = _bool_formatter(self.SaveExcludeMisVal)))
                OPTIONS.append(objectify.Element("SaveExcludeAllMisVal", value = _bool_formatter(self.SaveExcludeAllMisVal)))
                OPTIONS.append(objectify.Element("SaveExcludeConst", value = _bool_formatter(self.SaveExcludeConst)))
                OPTIONS.append(objectify.Element("SaveExcludeNearConst", value = _bool_formatter(self.SaveExcludeNearConst)))
                OPTIONS.append(objectify.Element("SaveExcludeStdDev", value = _bool_formatter(self.SaveExcludeStdDev)))
                OPTIONS.append(objectify.Element("SaveStdDevThreshold", value = self.SaveStdDevThreshold))
                OPTIONS.append(objectify.Element("SaveExcludeCorrelated", value = _bool_formatter(self.SaveExcludeCorrelated)))
                OPTIONS.append(objectify.Element("SaveCorrThreshold", value = self.SaveCorrThreshold))
                OPTIONS.append(objectify.Element("SaveExclusionOptionsToVariables", value = _bool_formatter(self.SaveExclusionOptionsToVariables)))
                OPTIONS.append(objectify.Element("SaveExcludeMisMolecules", value = _bool_formatter(self.SaveExcludeMisMolecules)))
                OPTIONS.append(objectify.Element("SaveExcludeRejectedMolecules", value = _bool_formatter(self.SaveExcludeRejectedMolecules)))
                OPTIONS.append(objectify.Element("RoundDescriptorValues", value = _bool_formatter(self.RoundDescriptorValues)))
         
                DESCRIPTORS = objectify.SubElement(self.dragon, "DESCRIPTORS")
                for i in self.blocks:
                    if i<1 or i>30:
                        msg = "block id must be in range 1 to 30."
                        raise ValueError(msg)
                    DESCRIPTORS.append(objectify.Element('block', id = "%i"%i, SelectAll = "true"))
        
                MOLFILES = objectify.SubElement(self.dragon, "MOLFILES")
                MOLFILES.append(objectify.Element("molInput", value = self.molInput))
                if self.molInput == "stdin":
                    if self.molInputFormat not in ['SYBYL','MDL','HYPERCHEM','SMILES','CML','MACROMODEL']:
                        msg = "'%s' is not a valid molInputFormat. Formats:['SYBYL','MDL','HYPERCHEM','SMILES','CML','MACROMODEL']"%self.molInputFormat
                        raise ValueError(msg) 
                    MOLFILES.append(objectify.Element("molInputFormat", value = self.molInputFormat)) 
                elif self.molInput == "file":
                    MOLFILES.append(objectify.Element("molFile", value = self.molFile)) 
                else:
                    msg = "Enter a valid molInput: 'stdin' or 'file'"
                    raise ValueError(msg)
                OUTPUT = objectify.SubElement(self.dragon, "OUTPUT")
                OUTPUT.append(objectify.Element("knimemode", value = _bool_formatter(self.knimemode)))
                OUTPUT.append(objectify.Element("SaveStdOut", value = _bool_formatter(self.SaveStdOut)))
                OUTPUT.append(objectify.Element("SaveProject", value = _bool_formatter(self.SaveProject)))
                if self.SaveProject:
                    OUTPUT.append(objectify.Element("SaveProjectFile", value = self.SaveProjectFile))
                OUTPUT.append(objectify.Element("SaveFile", value = _bool_formatter(self.SaveFile)))
                if self.SaveFile:
                    OUTPUT.append(objectify.Element("SaveType", value = self.SaveType)) # value = "[singlefile/block/subblock]"
                    OUTPUT.append(objectify.Element("SaveFilePath", value = self.output_directory+self.SaveFilePath)) #Specifies the file name for saving results as a plan text file(s), if the "singlefile" option is set; if "block" or "subblock" are set, specifies the path in which results files will be saved.
                OUTPUT.append(objectify.Element("logMode", value = self.logMode)) # value = [none/stderr/file]
                if self.logMode == "file":
                    OUTPUT.append(objectify.Element("logFile", value = self.output_directory+self.logFile))
            
                if self.external:
                    EXTERNAL = objectify.SubElement(self.dragon, "EXTERNAL") 
                    EXTERNAL.append(objectify.Element("fileName", value = self.fileName))
                    EXTERNAL.append(objectify.Element("delimiter", value = self.delimiter))
                    EXTERNAL.append(objectify.Element("consecutiveDelimiter", value = _bool_formatter(self.consecutiveDelimiter)))
                    EXTERNAL.append(objectify.Element("MissingValue", value = self.MissingValue))
                self._save_script()
                
            else:
                msg = "Only version 6 and version 7 (newest version) are available in this module."
                warnings.warn(msg,Warning)
        
        else:
            doc = etree.parse(script)
            self.dragon = etree.tostring(doc) 	# dragon script : dragon
            self.dragon = objectify.fromstring(self.dragon)
            objectify.deannotate(self.dragon)
            etree.cleanup_namespaces(self.dragon)
            if self.dragon.attrib['version'][0] not in ['6','7']:
                msg = "Dragon script is not labeled to the newest vesions of Dragon, 6 or 7. This may causes some problems."
                warnings.warn(msg,Warning)
            mandatory_nodes = ['OPTIONS','DESCRIPTORS','MOLFILES','OUTPUT']
            reported_nodes = [element.tag for element in self.dragon.iterchildren()]
            if not set(reported_nodes).issuperset(set(mandatory_nodes)):
                msg = 'Dragon script does not contain all mandatory nodes, which are:%s'%str(mandatory_nodes)
                raise ValueError(msg)
            self.drs = script
        self.data_path = self.dragon.OUTPUT.SaveFilePath.attrib['value']
        return self
        
    def _save_script(self): 
        objectify.deannotate(self.dragon)
        etree.cleanup_namespaces(self.dragon)
        self.drs_name = 'Dragon_script.drs'
        with open(self.output_directory+self.drs_name, 'w') as outfile:
            outfile.write("%s" %etree.tostring(self.dragon, pretty_print=True))

    def printout(self):
        objectify.deannotate(self.dragon)
        etree.cleanup_namespaces(self.dragon)
        print(objectify.dump(self.dragon))
        
    def run(self):
        print "running Dragon%s ..."%self.version    
        os.system('nohup dragon%sshell -s %s'%(self.version,self.output_directory+self.drs_name))
#         print subprocess.check_output(['nohup dragon%sshell -s %s'%(self.version,self.drs)])
        print "... Dragon job completed!"

# Copyright 2021 by DADON#4076 
# All rights reserved.
# This file is part of the Arcaea hacking efforts
# and is released under GPLv3 Please see the LICENSE
# https://www.gnu.org/licenses/gpl-3.0.en.html



import json
import os
import glob

#const
TRANSLATE_SKILL_NAME = 0
TRANSLATE_SKILL_DESC = 1
TRANSLATE_COMMON_NAMES = 2

#init dictionary and keylist
effectDict = {}
effectKeyList = {}
skillName = {}
skillNameKeyList = {}
skillDescription = {}
skillDescriptionKeyList = {}

#idk how you code if you don't know what the function name implies
def try_remove_files(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

#well, loading common list, but gonna rename them later. also should be merged with bottom one, just lazy for now
def load_effect_library(myjson, arrs):
    data = json.load(myjson)
    for group in data['Effect']:
        arrs[group["originEffect"]] = group["effect"]
    temp_list = {}
    # sorting this from longest length, cause we don't want to messed up with longer one
    for k in sorted(arrs, key=len, reverse=True):
        temp_list[k] = arrs[k]
    arrs = temp_list

#loading skill name, i haven't make auto conversion from fabulousgit, gonna implement that shit later
def load_skill_name_library(myjson, arrs):
    data = json.load(myjson)
    for group in data['skill_list']:
        arrs[group["text"]] = group["translation"]
    temp_list = {}
    # sorting this from longest length, cause we don't want to messed up with longer one
    for k in sorted(arrs, key=len, reverse=True):
        temp_list[k] = arrs[k]
    arrs = temp_list

#idem
def load_skill_desc_library(myjson, arrs):
    data = json.load(myjson)
    for group in data['skill-desc']:
        arrs[group["skill_description"]] = group["skill_translated"]
    temp_list = {}
    for k in sorted(arrs, key=len, reverse=True):
        temp_list[k] = arrs[k]
    arrs = temp_list

# TODO: gonna migrate this shit to translate_patch later. also i copied this function from stackoverflow (cause i never touch python until like month ago), so i gonna take a good look later
def get_all(myjson, key):
    if type(myjson) is dict:
        for jsonkey in myjson:
            if type(myjson[jsonkey]) in (list, dict):
                get_all(myjson[jsonkey], key)
            elif jsonkey == key:
                for dictList in effectKeyList:
                    myjson[jsonkey] = myjson[jsonkey].replace(dictList, effectDict[dictList])
                #print(myjson[jsonkey])
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                get_all(item, key)

def translate_patch(myjson, key, keyList, keyValueList):
    if type(myjson) is dict:
        for jsonkey in myjson:
            if type(myjson[jsonkey]) in (list, dict):
                translate_patch(myjson[jsonkey], key, keyList, keyValueList)
            elif jsonkey == key:
                for dictList in keyList:
                    myjson[jsonkey] = myjson[jsonkey].replace(dictList, keyValueList[dictList])
                #print(myjson[jsonkey])
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                translate_patch(item, key, keyList, keyValueList)

# TODO: gonna migrate this too into runPatchData
def runEffectPatchData(originalFile, temporaryFile, backupFile):
    with open(originalFile, "r+", encoding='utf-8') as f:
        currFile = json.loads(f.read())
        get_all(currFile,"Effect");
        with open(temporaryFile,"wb") as ff:
            ff.write(json.dumps(currFile, ensure_ascii=False, indent=4).encode('utf8'))
            ff.close()
        f.close()
        try_remove_files('./'+backupFile)
        os.rename(originalFile, backupFile)
        os.rename(temporaryFile, originalFile)

# gonna migrate that ifelseif into separate function, cause it's gonna be messy here if it's too large
def runPatchData(originalFile, temporaryFile, backupFile, key, patchType):
    with open(originalFile, "r+", encoding='utf-8') as f:
        currFile = json.loads(f.read())
        if (patchType == TRANSLATE_SKILL_NAME):
            translate_patch(currFile, key, skillNameKeyList, skillName)
        elif (patchType == TRANSLATE_SKILL_DESC):
            translate_patch(currFile, key, skillDescriptionKeyList, skillDescription)
        elif (patchType == TRANSLATE_COMMON_NAMES):
            translate_patch(currFile, key, effectKeyList, effectDict)
        with open(temporaryFile,"wb") as ff:
            ff.write(json.dumps(currFile, ensure_ascii=False, indent=4).encode('utf8'))
            ff.close()
        f.close()
        
        try_remove_files('./'+backupFile)
        os.rename(originalFile, backupFile)
        os.rename(temporaryFile, originalFile)

with open("UmaMusume_EffectTranslation.json", "r", encoding="utf-8-sig") as f:
    load_effect_library(f, effectDict)

with open("UmaMusume_SkillNameTranslation.json", "r", encoding="utf-8-sig") as f:
    load_skill_name_library(f, skillName)

with open("UmaMusume_SkillDescriptionTranslation.json", "r", encoding="utf-8-sig") as f:
    load_skill_desc_library(f, skillDescription)

effectKeyList = effectDict.keys()
skillNameKeyList = skillName.keys()
skillDescriptionKeyList = skillDescription.keys()

runPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryMainStory.json', 'UmaMusumeLibraryMainStoryTemp.json', 'UmaMusumeLibraryMainStoryBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryRevision.json', 'UmaMusumeLibraryRevisionTemp.json', 'UmaMusumeLibraryRevisionBackup.json', "Effect", TRANSLATE_SKILL_NAME)

runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Name", TRANSLATE_SKILL_NAME)
runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Effect", TRANSLATE_SKILL_DESC)
runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Effect", TRANSLATE_COMMON_NAMES)

runEffectPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json')
runEffectPatchData('UmaMusumeLibraryMainStory.json', 'UmaMusumeLibraryMainStoryTemp.json', 'UmaMusumeLibraryMainStoryBackup.json')
runEffectPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json')
runEffectPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json')
runEffectPatchData('UmaMusumeLibraryRevision.json', 'UmaMusumeLibraryRevisionTemp.json', 'UmaMusumeLibraryRevisionBackup.json')





                

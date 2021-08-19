# Copyright 2021 by DADON#4076 
# All rights reserved.
# This file is part of the Arcaea hacking efforts
# and is released under GPLv3 Please see the LICENSE
# https://www.gnu.org/licenses/gpl-3.0.en.html



import json
import os
import glob
from levenshtein import levenshtein_ratio_and_distance

#const
TRANSLATE_SKILL_NAME = 0
TRANSLATE_SKILL_DESC = 1
TRANSLATE_COMMON_NAMES = 2
TRANSLATE_UMA_NAMES = 3
TRANSLATE_UMA_TITLES = 4

#init dictionary and keylist
effectDict = {}
effectKeyList = {}
skillName = {}
skillNameKeyList = {}
skillDescription = {}
skillDescriptionKeyList = {}
umaName = {}
umaNameKeyList = {}
umaTitle = {}
umaTitleKeyList = {}

#idk how you code if you don't know what the function name implies
def try_remove_files(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def load_library(myjson, arrs, parent, key, keyValue):
    data = json.load(myjson)
    for group in data[parent]:
        arrs[group[key]] = group[keyValue]
    temp_list = {}
    for k in sorted(arrs, key=len, reverse=True):
        temp_list[k] = arrs[k]
    arrs = temp_list

def validate_leven_distance(origin, value):
    #Failsafe, must not more than 1 length difference
    if (abs(len(origin) - len(value) > 1)):
        return False
    if (min(len(origin), len(value)) < 7):
        return False
    distance = levenshtein_ratio_and_distance(origin, value)
    if (distance == 0):
        #this sound stupid, but if they're same, then there's a bug on replace shit. I doubt that would happen tho
        return False 
    return (min(len(origin), len(value)) / distance) > 8

# TODO: gonna migrate this shit to translate_patch later. also i copied this function from stackoverflow (cause i never touch python until like month ago), so i gonna take a good look later
def get_all(myjson, key,  isRunLeven = False):
    if type(myjson) is dict:
        for jsonkey in myjson:
            if type(myjson[jsonkey]) in (list, dict):
                get_all(myjson[jsonkey], key, isRunLeven)
            elif jsonkey == key:
                #Mark if it's patched so it wont interfere with semi-translated shit
                markPatched = False
                for dictList in effectKeyList:
                    if (dictList in myjson[jsonkey]):
                        markPatched = True
                        myjson[jsonkey] = myjson[jsonkey].replace(dictList, effectDict[dictList])
                    if ((isRunLeven == True) and (markPatched == False) and validate_leven_distance(myjson[jsonkey], dictList) == True):
                        myjson[jsonkey] = effectDict[dictList]
                #print(myjson[jsonkey])
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                get_all(item, key, isRunLeven)

def translate_patch(myjson, key, keyList, keyValueList, isRunLeven = False):
    if type(myjson) is dict:
        for jsonkey in myjson:
            if type(myjson[jsonkey]) in (list, dict):
                translate_patch(myjson[jsonkey], key, keyList, keyValueList, isRunLeven)
            elif jsonkey == key:
                #Mark if it's patched so it wont interfere with semi-translated shit
                markPatched = False
                for dictList in keyList:
                    if (dictList in myjson[jsonkey]):
                        markPatched = True
                        myjson[jsonkey] = myjson[jsonkey].replace(dictList, keyValueList[dictList])
                    if ((isRunLeven == True) and (markPatched == False) and validate_leven_distance(myjson[jsonkey], dictList) == True):
                        myjson[jsonkey] = keyValueList[dictList]
                #print(myjson[jsonkey])
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                translate_patch(item, key, keyList, keyValueList, isRunLeven)

def uma_name_patching(myjson, key, keyValue, isRunLeven = False):
    if type(myjson) is dict:
        for jsonkey in myjson.copy():
            if key in jsonkey:
                #print(key)
                temp_key = jsonkey.replace(key, keyValue)
                myjson[temp_key] = myjson[jsonkey]
                del myjson[jsonkey]
            elif (isRunLeven == True and validate_leven_distance(key, jsonkey)):
                temp_key = keyValue
                myjson[temp_key] = myjson[jsonkey]
                del myjson[jsonkey]
            elif type(myjson[jsonkey]) in (list, dict):
                uma_name_patching(myjson[jsonkey], key, keyValue, isRunLeven)
                #print(myjson[jsonkey])
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                uma_name_patching(item, key, keyValue, isRunLeven)

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
            translate_patch(currFile, key, skillDescriptionKeyList, skillDescription, True)
        elif (patchType == TRANSLATE_COMMON_NAMES):
            translate_patch(currFile, key, effectKeyList, effectDict)
        elif (patchType == TRANSLATE_UMA_NAMES):
            for umaKeys in umaNameKeyList:
                uma_name_patching(currFile, umaKeys, umaName[umaKeys])
        elif (patchType == TRANSLATE_UMA_TITLES):
            for umaKeys in umaTitleKeyList:
                uma_name_patching(currFile, umaKeys, umaTitle[umaKeys])
        with open(temporaryFile,"wb") as ff:
            ff.write(json.dumps(currFile, ensure_ascii=False, indent=4).encode('utf8'))
            ff.close()
        f.close()
        
        try_remove_files('./'+backupFile)
        os.rename(originalFile, backupFile)
        os.rename(temporaryFile, originalFile)

with open("UmaMusume_EffectTranslation.json", "r", encoding="utf-8-sig") as f:
    load_library(f, effectDict, 'Effect', 'originEffect', 'effect')

with open("UmaMusume_SkillNameTranslation.json", "r", encoding="utf-8-sig") as f:
    load_library(f, skillName , 'skill_list', 'text', 'translation')

with open("UmaMusume_SkillDescriptionTranslation.json", "r", encoding="utf-8-sig") as f:
    load_library(f, skillDescription, 'skill-desc', 'skill_description', 'skill_translated')

with open("UmaMusume_UmaNameTranslation.json", "r", encoding="utf-8-sig") as f:
    load_library(f, umaName, 'uma-name', 'text', 'translation')

with open("UmaMusume_UmaTitleTranslation.json", "r", encoding="utf-8-sig") as f:
    load_library(f, umaTitle, 'uma-title', 'text', 'translation')

effectKeyList = effectDict.keys()
skillNameKeyList = skillName.keys()
skillDescriptionKeyList = skillDescription.keys()
umaNameKeyList = umaName.keys()
umaTitleKeyList = umaTitle.keys()

runPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryMainStory.json', 'UmaMusumeLibraryMainStoryTemp.json', 'UmaMusumeLibraryMainStoryBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json', "Effect", TRANSLATE_SKILL_NAME)
runPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json', "Effect", TRANSLATE_SKILL_NAME)
print("Part 1 Finished")

#the file is gone wtf
#runPatchData('UmaMusumeLibraryRevision.json', 'UmaMusumeLibraryRevisionTemp.json', 'UmaMusumeLibraryRevisionBackup.json', "Effect", TRANSLATE_SKILL_NAME)

runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Name", TRANSLATE_SKILL_NAME)
runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Effect", TRANSLATE_SKILL_DESC)
runPatchData('SkillLibrary.json', 'SkillLibraryTemp.json', 'SkillLibraryBackup.json', "Effect", TRANSLATE_COMMON_NAMES)
print("Part 2 Finished")


runPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json', "Effect", TRANSLATE_UMA_NAMES)
runPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json', "Effect", TRANSLATE_UMA_NAMES)
runPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json', "Effect", TRANSLATE_UMA_NAMES)
runPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json', "Effect", TRANSLATE_UMA_TITLES)
runPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json', "Effect", TRANSLATE_UMA_TITLES)
runPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json', "Effect", TRANSLATE_UMA_TITLES)
print("Part 3 Finished")

runEffectPatchData('UmaMusumeLibrary.json', 'UmaMusumeLibraryTemp.json', 'UmaMusumeLibraryBackup.json')
runEffectPatchData('UmaMusumeLibraryMainStory.json', 'UmaMusumeLibraryMainStoryTemp.json', 'UmaMusumeLibraryMainStoryBackup.json')
runEffectPatchData('UmaMusumeLibraryModify.json', 'UmaMusumeLibraryModifyTemp.json', 'UmaMusumeLibraryModifyBackup.json')
runEffectPatchData('UmaMusumeLibraryOrigin.json', 'UmaMusumeLibraryOriginTemp.json', 'UmaMusumeLibraryOriginBackup.json')
print("Part 4 Finished")
#the file is gone wtf
#runEffectPatchData('UmaMusumeLibraryRevision.json', 'UmaMusumeLibraryRevisionTemp.json', 'UmaMusumeLibraryRevisionBackup.json')




                

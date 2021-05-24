# StartingPointsUtil
# MODDER READ THIS:
# You do not have to change anything in this file
# all changes have to be done in the CvEventManager.
# This file just has to be in the same folder like the CvEventManager.py.

from CvPythonExtensions import *
import sys
import CvUtil
gc = CyGlobalContext()
SpawnCivList = []
BarbCityList = []
UsedValidCivList = []

# generic file reading function
def ReadMyFile(MyFile, Debugging, AddPositionsToMap, bPlaceCivs, bPlaceBarbCities):
    del SpawnCivList[:]
    del UsedValidCivList[:]
    del BarbCityList[:]
    CurCiv = None
    BarbCity = None
    if Debugging:
        print("preparing to read")
    for CurString in MyFile.readlines():
        if "CIVILIZATION_" in CurString:
            if CurCiv is not None:
                SpawnCivList.append(CurCiv)
            CurCiv = SpawningCiv()
            CurCiv.CivString = CutString(CurString)
        elif "StartX" in CurString:
            CurCiv.SpawnX.append(int(CutString(CurString)))
        elif "StartY" in CurString:
            CurCiv.SpawnY.append(int(CutString(CurString)))
            # SpawnCivList.append(CurCiv)
        elif "BarbCityName" in CurString:
            BarbCity = BarbarianCity()
            BarbCity.CityName = CutString(CurString)
        elif "BarbCityX" in CurString:
            BarbCity.CityX = (int(CutString(CurString)))
        elif "BarbCityY" in CurString:
            BarbCity.CityY = (int(CutString(CurString)))
        elif "BarbCityPopulation" in CurString:
            BarbCity.CityPopulation = (int(CutString(CurString)))
        elif "BarbCityNumDefenders" in CurString:
            BarbCity.CityNumDefenders = (int(CutString(CurString)))
            BarbCityList.append(BarbCity)
    # add last Civ to SpawnCivList
    if CurCiv is not None:
        SpawnCivList.append(CurCiv)
    if Debugging:
        print("all civs have been read")
    if bPlaceCivs:
        ResortCivs(Debugging)
    if bPlaceBarbCities:
        PlaceBarbarianCities(Debugging)
    if AddPositionsToMap:
        AddCoordinateSignsToMap()

# core function for resorting civs on the map
def ResortCivs(Debugging):
    iMaxPlayer = gc.getMAX_CIV_PLAYERS()
    iMaxLoadedPlayer = len(SpawnCivList)
    lHumanPlayers = []
    CounterInvalid = 0
# loop detects human players
    for ip in range(iMaxPlayer):
        CurPlayer = gc.getPlayer(ip)
        if CurPlayer.isHuman():
            lHumanPlayers.append(ip)
    iHumanPlayer = lHumanPlayers[0]
    if Debugging:
        CyInterface().addMessage(iHumanPlayer, False, 15, "Beginning to resort civs", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
    if Debugging:
        print("Beginning to resort civs")
    if not HumanPlayerIsValidCiv(lHumanPlayers, iMaxLoadedPlayer):
        CyInterface().addMessage(iHumanPlayer, False, 15, "Invalid Civ for map has been chosen!!!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
        CyInterface().addMessage(iHumanPlayer, False, 15, "Civs will not start at correct positions!!!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
        return

# following loop moves all the units off the map
# it prevents accidential contacts
# PAE: except Barbarian Units
    for iMoveAway in range(iMaxPlayer):
        if iMoveAway != gc.getBARBARIAN_PLAYER():
            pLoopCiv = gc.getPlayer(iMoveAway)
            if pLoopCiv and not pLoopCiv.isNone() and pLoopCiv.isAlive():  # only valid players
                print "pLoopCiv %s" %(pLoopCiv.getName())
                (loopUnit, pIter) = pLoopCiv.firstUnit(False)
                while(loopUnit):
                    unitOwner = loopUnit.getOwner()
                    
                    if not loopUnit.isNone() and loopUnit.getOwner() == pLoopCiv.getID():  # only valid units
                        #loopUnit.setXY(-1,-1, False,False,False)
                        print "loopUnit %s" %(loopUnit.getName())
                        loopUnit.setXY(1,1, False, False, False)
                        #loopUnit.setXY(gc.getINVALID_PLOT_COORD(), gc.getINVALID_PLOT_COORD(), False, False, False)
                        
                        print "loopUnit moved %s" %(loopUnit.getName())
                    (loopUnit, pIter) = pLoopCiv.nextUnit(pIter, False)
            
    print "PAE: except Barbarian Units" 

# this loop replaces the current units/moves them to the right place
# invalid civs are killed, and the number is counted
# IDs of used/invalid civs are stored in a global list, so that
# adding new ones is easier
    aPosUsed = []
    for i in xrange(iMaxPlayer):
        if i != gc.getBARBARIAN_PLAYER():
            pLoopCiv = gc.getPlayer(i)
            if Debugging:
                CyInterface().addMessage(iHumanPlayer, False, 15, "Got a civ!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            if Debugging:
                print("Got a civ!")
            if not pLoopCiv.isAlive():
                continue
            iLoopCivName = pLoopCiv.getCivilizationType()
            for j in xrange(iMaxLoadedPlayer):
                if Debugging:
                    CyInterface().addMessage(iHumanPlayer, False, 15, "Cycling loaded coordinates!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
                if Debugging:
                    print("Cycling loaded coordinates!")
                if iLoopCivName == gc.getInfoTypeForString(SpawnCivList[j].CivString):
                    if Debugging:
                        CyInterface().addMessage(iHumanPlayer, False, 15, "Preparing for re-placing current units!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
                    if Debugging:
                        print("Preparing for re-placing current units!")

                    possible_plot_idx = [i for i, p in enumerate(zip(SpawnCivList[j].SpawnX,SpawnCivList[j].SpawnY)) if p not in aPosUsed]
                    # possible_plot_idx = freePositions(SpawnCivList[j], aPosUsed)

                    if SpawnCivList[j].SpawnX[0] == -1 or SpawnCivList[j].SpawnY[0] == -1 or not possible_plot_idx:
                        CounterInvalid += 1
                        if Debugging:
                            CyInterface().addMessage(iHumanPlayer, False, 15, "Counter invalid civs "+str(CounterInvalid), '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
                        (loopUnit, pIter) = pLoopCiv.firstUnit(False)
                        while loopUnit:
                            unitOwner = loopUnit.getOwner()
                            if not loopUnit.isNone() and loopUnit.getOwner() == pLoopCiv.getID():  # only valid units
                                loopUnit.setXY(1, 1, False, False, False)
                            (loopUnit, pIter) = pLoopCiv.nextUnit(pIter, False)
                        pLoopCiv.killUnits()
                        continue
                    else:
                        UsedValidCivList.append(iLoopCivName)

                    iPos = possible_plot_idx[0]

                    #iNumPositions = len(SpawnCivList[j].SpawnX)
                    #if SpawnCivList[j].timesUsed >= iNumPositions - 1:
                    #    iPos = iNumPositions - 1
                    #else:
                    #    iPos = SpawnCivList[j].timesUsed
                    iX = SpawnCivList[j].SpawnX[iPos]
                    iY = SpawnCivList[j].SpawnY[iPos]
                    aPosUsed.append((iX,iY))
                    SpawnCivList[j].timesUsed += 1
                    (loopUnit, pIter) = pLoopCiv.firstUnit(False)
                    while loopUnit:
                        unitOwner = loopUnit.getOwner()
                        if not loopUnit.isNone() and loopUnit.getOwner() == pLoopCiv.getID():  # only valid units

                            loopUnit.setXY(iX, iY, False, False, False)
                            if Debugging:
                                idstring = pLoopCiv.getCivilizationAdjective(0)+"unit moved to X="+str(iX)+"and Y="+str(iY)
                                print(idstring)
                                CyInterface().addMessage(iHumanPlayer, False, 15, idstring, '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), iY, iY, True, True)
                        (loopUnit, pIter) = pLoopCiv.nextUnit(pIter, False)
    # PAE change: check if CounterInvalid > 0
    # PAE: do not replace missing civ
    if CounterInvalid > 0:
        AddMissingCivs(CounterInvalid, iMaxLoadedPlayer, iMaxPlayer, Debugging)
    FlushVisibleArea()

## funktioniert nicht richtig
# def freePositions(civ, aPosUsed):
    
    # min_d = 1
    # possible = []
    # impossible = []
    # for i, p in enumerate(zip(civ.SpawnX,civ.SpawnY)):
        # if p[0] != -1 and p[1] != -1:
            # for occupied_plot in aPosUsed:
                # dx = abs(p[0]-occupied_plot[0])
                # dy = abs(p[1]-occupied_plot[1])
                # d = max(dx,dy) + min(dx,dy)/2
                # if d < min_d:
                    # impossible.append(i)
                # if d >= min_d:
                    # possible.append(i)
    # possible = set(possible).symmetric_difference(impossible)
    # return possible

# place barbarian cities
def PlaceBarbarianCities(BarbCityList, Debugging):
    pBarb = gc.getPlayer(gc.getBARBARIAN_PLAYER())
    for BarbCity in BarbCityList:
        iX = BarbCity.CityX
        iY = BarbCity.CityY
        pCity = pBarb.initCity(iX, iY)
        pCity.setName(BarbCity.CityName, 0)
        pCity.setPopulation(BarbCity.CityPopulation)
        eWarrior = gc.getInfoTypeForString("UNIT_WARRIOR")
        for i in range(BarbCity.CityNumDefenders):
            pBarb.initUnit(eWarrior, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
    FlushVisibleArea()


# checks, if the human players have selected a valid civ for the map
def HumanPlayerIsValidCiv(lHumanPlayers, iMaxLoadedPlayer):
    for iHumanPlayer in lHumanPlayers:
        pHumanPlayer = gc.getPlayer(iHumanPlayer)
        iHumanName = pHumanPlayer.getCivilizationType()
        for iCivs in xrange(iMaxLoadedPlayer):
            if iHumanName == gc.getInfoTypeForString(SpawnCivList[iCivs].CivString):
                if SpawnCivList[iCivs].SpawnX[0] == -1 or SpawnCivList[iCivs].SpawnY[0] == -1:
                    return False
                else:
                    break
        else:
            return False
    else:
        return True

# makes the old starting positions invisible for the teams
def FlushVisibleArea():
    iMaxX = CyMap().getGridWidth()
    iMaxY = CyMap().getGridHeight()
    iMaxTeam = gc.getMAX_CIV_TEAMS()
    for iX in xrange(iMaxX):
        for iY in xrange(iMaxY):
            pPlot = CyMap().plot(iX, iY)
            for iTeams in xrange(iMaxTeam):
                if not pPlot.isVisible(iTeams, False):
                    pPlot.setRevealed(iTeams, False, False, iTeams)

# adds signs with the coordinates to the map
# so that potential starting positions can easier be modified
def AddCoordinateSignsToMap():
    iMaxX = CyMap().getGridWidth()
    iMaxY = CyMap().getGridHeight()
    iMaxPlayer = gc.getMAX_CIV_PLAYERS()
    iHumanPlayer = -1
    for iCivs in xrange(iMaxPlayer):
        pPlayer = gc.getPlayer(iCivs)
        if pPlayer.isHuman():
            iHumanPlayer = iCivs
            break
    for iX in xrange(iMaxX):
        for iY in xrange(iMaxY):
            pPlot = CyMap().plot(iX, iY)
            PrintString = "X = "+str(iX)+" Y = "+str(iY)
            CyEngine().addSign(pPlot, iHumanPlayer, PrintString)

# next 2 functions add new civs for the invalid chosen ones to the map
def AddMissingCivs(CounterInvalid, iMaxLoadedPlayer, iMaxPlayer, Debugging):
    iAllCivs = gc.getNumPlayableCivilizationInfos()
    CounterCycles = 0
    iMaxValid = 0
    for i in range(len(SpawnCivList)):
        if SpawnCivList[i].SpawnX[0] == -1 or SpawnCivList[i].SpawnY[0] == -1:
            continue
        else:
            iMaxValid = iMaxValid+1
    if Debugging:
        print("valid civs for this map: "+str(iMaxValid))
        print("max civs: "+str(iMaxPlayer))
    while True:
        if Debugging:
            print("trying to add a civ")
        CounterCycles = CounterCycles+1
        if CounterCycles >= 100:
            break
        if AddThisCiv(iAllCivs, CounterInvalid, iMaxLoadedPlayer, iMaxPlayer, iMaxValid, Debugging):
            CounterInvalid = CounterInvalid-1
            if Debugging:
                print("added 1 civ")
        if CounterInvalid <= 0:
            return


def AddThisCiv(iAllCivs, CounterInvalid, iMaxLoadedPlayer, iMaxPlayer, iMaxValid, Debugging):
    iCivID = -1
    iMaxUsed = len(UsedValidCivList)
    for i in xrange(iMaxPlayer):
        pLoopCiv = gc.getPlayer(i)
        if pLoopCiv.getNumUnits() == 0:
            iCivID = i
            break
    else:
        return False

    for iCivs in xrange(iAllCivs):
        IsInList = False
        for iUsedCivs in xrange(iMaxUsed):
            if UsedValidCivList[iUsedCivs] == iCivs:
                IsInList = True
                break
        if IsInList:
            continue
        if not IsInList:
            if Debugging:
                print("adding new civ")
            for j in xrange(iMaxLoadedPlayer):
                if gc.getInfoTypeForString(SpawnCivList[j].CivString) == iCivs:
                    if SpawnCivList[j].SpawnX[0] == -1 or SpawnCivList[j].SpawnY[0] == -1:
                        UsedValidCivList.append(iCivs)
                        return False
                    else:
                        if iMaxValid > iMaxPlayer:
                            UseIt = gc.getGame().getMapRand().get(10, "Will i use this civ, o oracle?")
                            if UseIt == 1:
                                return False
                        UsedValidCivList.append(iCivs)
                        CurCiv = gc.getCivilizationInfo(iCivs)
                        NumLeaders = CurCiv.getNumLeaders()
                        dice = gc.getGame().getMapRand()
                        LeaderNum = dice.get(NumLeaders, "OracleSayMeTheLeader")
                        LeaderCounter = 0
                        for iLeaders in range(gc.getNumLeaderHeadInfos()):
                            if CurCiv.isLeaders(iLeaders):
                                if NumLeaders == 1:
                                    NewLeaderID = iLeaders
                                    break
                                else:
                                    if LeaderCounter == LeaderNum:
                                        NewLeaderID = iLeaders
                                        break
                                    LeaderCounter = LeaderCounter+1
                        CyGame().addPlayer(iCivID, NewLeaderID, iCivs)
                        AddTechsAndUnits(iCivID, j, CurCiv)
                        return True

# adds starting techs/techs from difficulty level/starting units/units from difficulty leven
# to the map, because just adding a player will give a civ really completly nothing
def AddTechsAndUnits(iCivID, j, CurCiv):
    ThisPlayer = gc.getPlayer(iCivID)
    ThisPlayer.initUnit(gc.getInfoTypeForString("UNIT_SETTLER"), SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
    ThisPlayer.initUnit(gc.getInfoTypeForString("UNIT_WARRIOR"), SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
    ThisTeam = gc.getTeam(ThisPlayer.getTeam())
    DifficultyLevel = gc. getHandicapInfo(CyGame().getHandicapType())
    iWorkers = DifficultyLevel.getAIStartingWorkerUnits()
    for iWorkUnits in xrange(iWorkers):
        iCivWorker = CurCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_WORKER"))
        ThisPlayer.initUnit(iCivWorker, SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
    iArchers = DifficultyLevel.getAIStartingDefenseUnits()
    for iArcher in xrange(iArchers):
        iCivArcher = CurCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ARCHER"))
        ThisPlayer.initUnit(iCivArcher, SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
    iScouts = DifficultyLevel.getAIStartingExploreUnits()
    for iScout in xrange(iScouts):
        iCivScout = CurCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SCOUT"))
        ThisPlayer.initUnit(iCivScout, SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
    iSettlers = DifficultyLevel.getAIStartingUnitMultiplier()
    for iSettler in xrange(iSettlers):
        iCivSettler = CurCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SETTLER"))
        ThisPlayer.initUnit(iCivSettler, SpawnCivList[j].SpawnX[0], SpawnCivList[j].SpawnY[0], UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)

    iNumTechs = gc.getNumTechInfos()
    for iTechs in xrange(iNumTechs):
        if DifficultyLevel.isAIFreeTechs(iTechs) > 0 or CurCiv.isCivilizationFreeTechs(iTechs):
            ThisTeam.setHasTech(iTechs, True, iCivID, False, False)

    return

# generic string cutting function
# first < and > at the end are cut of, then the other
# > and < are searched, and what is between is used as value
def CutString(string):
    # print("Cutting")
    string = str(string)
    string = string.strip()
    string = string[2:-1]
    BeginPos = -1
    EndPos = -1
    for i in xrange(len(string)):
        if string[i] == ">":
            BeginPos = i
        elif string[i] == "<":
            EndPos = i
            break
    else:
        return "-1"
    NewString = string[BeginPos+1:EndPos]
    return str(NewString)


def findStartingPlot(playerID):
   
    print("findStartingPlot for player %d" %(playerID))
    CyInterface().addMessage(playerID, False, 15, "Beginning to resort civs", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            

    
    if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START) or gc.getGame().getGameTurnYear() != gc.getDefineINT("START_YEAR") or sScenarioName not in MapNames:
        CyPythonMgr().allowDefaultImpl()
        print("allowDefaultImpl")
        return
    else:
        del SpawnCivList[:]
        del UsedValidCivList[:]
        del BarbCityList[:]
        CurCiv = None
        BarbCity = None
        MapName = mapNames(sScenarioName)
        bPlaceBarbCities = False
        Debugging = True
        AddPositionsToMap = True
        pPlayer = gc.getPlayer(playerID)
        if Debugging:
            print("preparing to read")
        
        iMaxValid = sum(1 for pCiv in SpawnCivList if pCiv.SpawnX[0] != -1 and pCiv.SpawnY[0] != -1)
        # iMaxValid = 0
        # for pCiv in SpawnCivList:
            # if pCiv.SpawnX[0] != -1 and pCiv.SpawnY[0] != -1:
                # iMaxValid += 1
        if Debugging:
            print("valid civs for this map: "+str(iMaxValid))
            print("max civs: "+str(iMaxPlayer))
        
        if Debugging:
            print("all civs have been read")
            
        # loop detects human players
        lHumanPlayers = []
        for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
            if gc.getPlayer(iPlayer).isHuman():
                lHumanPlayers.append(iPlayer)
        iHumanPlayer = lHumanPlayers[0]
        
        if Debugging:
            CyInterface().addMessage(iHumanPlayer, False, 15, "Beginning to resort civs", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            print("Beginning to resort civs")

        iPlayerCiv = pPlayer.getCivilizationType()
        if pPlayer.isHuman() and (iPlayerCiv not in SpawnCivList or SpawnCivList[iPlayerCiv].SpawnX[0] == -1 or SpawnCivList[iPlayerCiv].SpawnY[0] == -1):
            CyInterface().addMessage(iHumanPlayer, False, 15, "Invalid Civ for map has been chosen", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            CyInterface().addMessage(iHumanPlayer, False, 15, "Civs will not start at correct positions", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            CyPythonMgr().allowDefaultImpl()
            print("Invalid Civ for map has been chosen")
            return 

        if not pPlayer.isAlive():
            CyInterface().addMessage(iHumanPlayer, False, 15, "Player %d is not alive!" %(playerID), '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            CyPythonMgr().allowDefaultImpl()
            print("Player %d is not alive!" %(playerID))
            return
        # this loop replaces the current units/moves them to the right place
        # invalid civs are replaced
        # IDs of used/invalid civs are stored in a global list, so that
        # adding new ones is easier
        aPosUsed = []
        
        if Debugging:
            CyInterface().addMessage(iHumanPlayer, False, 15, "Cycling loaded coordinates!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            print("Cycling loaded coordinates!")
        
    
        if Debugging:
            CyInterface().addMessage(iHumanPlayer, False, 15, "Preparing for re-placing current units!", '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
            print("Preparing for re-placing current units!")
        bReplace = False
        bSpawn = False
        if iPlayerCiv not in SpawnCivList:
            bReplace = True
        else:
            pCiv = SpawnCivList[iPlayerCiv]
            possible_plot_idx = [i for i, p in enumerate(zip(pCiv.SpawnX,pCiv.SpawnY)) if p not in aPosUsed]
            if pCiv.SpawnX[0] == -1 or pCiv.SpawnY[0] == -1 or not possible_plot_idx:
                bReplace = True
                if Debugging:
                    CyInterface().addMessage(iHumanPlayer, False, 15, "Encountered invalid civ "+str(pCiv.CivString), '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True, True)
        if bReplace:                    
            (iNewCiv, iNewLeader) = ChangeThisCiv(CounterInvalid, SpawnCivList, iMaxPlayer, iMaxValid, Debugging)
            if iNewCiv:
                pCiv = SpawnCivList[iNewCiv]
                possible_plot_idx = [i for i, p in enumerate(zip(pCiv.SpawnX,pCiv.SpawnY)) if p not in aPosUsed]
                pPlayer.changeCiv(iNewCiv)
                pPlayer.changeCiv(iNewLeader)
                bSpawn = True
                UsedValidCivList.append(iNewCiv)
            else:
                # failed to find a possible replacement civs

                (loopUnit, pIter) = pPlayer.firstUnit(False)
                while loopUnit:
                    if not loopUnit.isNone() and loopUnit.getOwner() == pPlayer.getID():  # only valid units
                        loopUnit.setXY(1, 1, False, False, False)
                    (loopUnit, pIter) = pPlayer.nextUnit(pIter, False)
                pPlayer.killUnits()
        else:
            pCiv = SpawnCivList[iPlayerCiv]
            bSpawn = True
            UsedValidCivList.append(iPlayerCiv)
            
        plotIdx = -1
        if bSpawn:
            iPos = possible_plot_idx[gc.getSorenRandNum(len(possible_plot_idx)), "Select starting plot"]

            iX = pCiv.SpawnX[iPos]
            iY = pCiv.SpawnY[iPos]
            aPosUsed.append((iX,iY))
            pCiv.timesUsed += 1
            # plotIdx = CyMap().plotNum(iX, iY)
            # move existing units to proper spot
            # (loopUnit, pIter) = pLoopCiv.firstUnit(False)
            # while loopUnit:
                # unitOwner = loopUnit.getOwner()
                # if not loopUnit.isNone() and loopUnit.getOwner() == pLoopCiv.getID():  # only valid units

                    # loopUnit.setXY(iX, iY, False, False, False)
                    # if Debugging:
                        # idstring = pLoopCiv.getCivilizationAdjective(0)+"unit moved to X="+str(iX)+"and Y="+str(iY)
                        # print(idstring)
                        # CyInterface().addMessage(iHumanPlayer, False, 15, idstring, '', 0, 'Art/Interface/Buttons/General/warning_popup.dds', ColorTypes(gc.getInfoTypeForString("COLOR_RED")), iY, iY, True, True)
                # (loopUnit, pIter) = pLoopCiv.nextUnit(pIter, False)

        if bPlaceBarbCities:
            PlaceBarbarianCities(Debugging)
        if AddPositionsToMap:
            AddCoordinateSignsToMap()
            
        # return plotIdx
        return (iX, iY)

class SpawningCiv:
    def __init__(self):
        self.CivString = 0
        self.SpawnX = []
        self.SpawnY = []
        self.timesUsed = 0


class BarbarianCity:

    def __init__(self):
        self.CityName = 0
        self.CityX = 0
        self.CityY = 0
        self.CityPopulation = 1
        self.CityNumDefenders = 0

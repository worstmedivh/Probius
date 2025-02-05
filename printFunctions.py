from aliases import *
import asyncio
import re
from discordIDs import *

allHeroes={
	'bruiser':['Artanis', 'Chen', 'D.Va', 'Deathwing', 'Dehaka', 'Gazlowe', 'Hogger','Imperius', 'Leoric', 'Malthael', 'Ragnaros', 'Rexxar', 'Sonya', 'Thrall', 'Varian', 'Xul', 'Yrel'],
	'healer':['Alexstrasza', 'Ana', 'Anduin', 'Auriel', 'Brightwing', 'Deckard', 'Kharazim', 'Li_Li', 'Lt._Morales', 'Lúcio', 'Malfurion', 'Rehgar', 'Stukov', 'Tyrande', 'Uther', 'Whitemane'],
	'mage':['Azmodan', 'Chromie', 'Gall', "Gul'dan", 'Jaina', "Kael'thas", "Kel'Thuzad", 'Li-Ming', 'Mephisto', 'Nazeebo', 'Orphea', 'Probius', 'Tassadar'],
	'marksman':['Cassia', 'Falstad', 'Fenix', 'Genji', 'Greymane', 'Hanzo', 'Junkrat', 'Lunara', 'Nova', 'Raynor', 'Sgt._Hammer', 'Sylvanas', 'Tracer', 'Tychus', 'Valla', 'Zagara',"Zul'jin"],
	'melee':['Alarak', 'Illidan', 'Kerrigan', 'Maiev', 'Murky', 'Qhira', 'Samuro', 'The_Butcher', 'Valeera', 'Zeratul'],
	'support':['Abathur', 'Medivh', 'The_Lost_Vikings', 'Zarya'],
	'tank':["Anub'arak", 'Arthas', 'Blaze', 'Cho', 'Diablo', 'E.T.C.', 'Garrosh', 'Johanna', "Mal'Ganis", 'Mei', 'Muradin', 'Stitches', 'Tyrael']
}

def getHeroes():#Returns an alphabetically sorted list of all allHeroes.
	return sorted([j for i in allHeroes.values() for j in i])

async def getRoleHeroes(role):
	if role=='ranged':
		return allHeroes['mage']+allHeroes['marksman']
	elif role=='assassin':
		return (await getRoleHeroes('ranged'))+allHeroes['melee']
	else:
		return allHeroes[role]

async def heroes(message,text,channel,client):
	#['hero', 'heroes', 'bruiser', 'healer', 'support', 'ranged', 'melee', 'assassin', 'mage', 'marksman', 'tank']
	role=text[0].replace('marksmen','marksman').replace('offlaner','bruiser')
	if role[-1]=='s':role=role[:-1]
	if len(text)==1:
		if role in ['hero', 'heroe']:
			await channel.send('\n'.join(['**'+i.capitalize()+':** '+', '.join(allHeroes[i]).replace('_',' ') for i in allHeroes]))
		elif role=='assassin':
			await channel.send('\n'.join(['**'+i.capitalize()+':** '+', '.join(allHeroes[i]).replace('_',' ') for i in ['mage', 'marksman', 'melee']]))
		elif role=='ranged':
			await channel.send('\n'.join(['**'+i.capitalize()+':** '+', '.join(allHeroes[i]).replace('_',' ') for i in ['mage', 'marksman']]))
		else:
			await channel.send('**'+role.capitalize()+':** '+', '.join(allHeroes[role]).replace('_',' '))
	else:
		if role in ['hero', 'heroe']:
			await printAll(client,message,text[1])
		else:
			await printAll(client,message,text[1], 1, await getRoleHeroes(role))
def printTier(talents,tier):#Print a talent tier
	output=''
	for i in talents[tier]:
		output+=i+'\n'
	return output

def printAbility(abilities,hotkey):#Prints abilities with matching hotkey
	output=''
	for ability in abilities:
		if '**['+hotkey.upper()+']' in ability:
			output+=ability+'\n'
	return output

def deepAndShallowSearchFoundBool(ability,string,deep):#Python3.5 doesn't allow async functions inside list comprehension :(
	if not deep:
		ability=ability.split(':**')[0]
	if string in ability.lower():
		return 1

	if string==''.join([i[0] for i in ability.lower().split(':**')[0].split(' ')[1:]]):
		return 1
	return 0

async def printCompactBuild(client,channel,text):
	#bot channel: posts whole thing
	#outside bot channel: post formatted query and name of talents, and reacts :thumb up:
	#when reacted to, print whole thing
	build,hero=text.split(',')#Example: T0230303,DVa
	hero=aliases(hero)
	(abilities,talents)=client.heroPages[hero]
	build=build.replace('q','1').replace('w','2').replace('e','3').replace('r','4').replace('t','5')

	#Check for malicious input, since the build will be repeated back
	for i in build[1:]:
		if i not in '0123456789':return

	if channel.id in client.botChannels.values():
		await printBuild(channel,build,talents)
		return

	output='Talent build [T'+build[1:]+','+hero+']: '
	talentsToPrint=[]
	for j,i in enumerate(build[1:]):
		if i=='0':continue
		talentsToPrint.append(talents[j][int(i)-1].split('**')[1].split('] ')[1].replace(':',''))
	output+=', '.join(talentsToPrint)
	message=await channel.send(output)
	await message.add_reaction('👍')

async def printBuild(channel,build,talents):#Posts all tooltips on reactions, or when posted in bot channel
	output=[]
	for j,i in enumerate(build[1:]):
		if i=='0':continue
		output.append(talents[j][int(i)-1])
	await printLarge(channel,'\n'.join(output))

async def printBuildFromReaction(client,message):
	build,hero=message.content.split('[')[1].split(']')[0].split(',')
	(abilities,talents)=client.heroPages[hero]
	await printBuild(message.channel,build,talents)

async def addUnderscoresAndNewline(namelist,ability):
	indices=[]
	for i in namelist:
		#ability=ability.replace(i,'__'+i+'__').replace(i.capitalize(),'__'+i.capitalize()+'__').replace(i.title(),'__'+i.title()+'__')
		indicesA=[m.start() for m in re.finditer(i,ability.lower())]
		indices+=[j+len(i) for j in indicesA]+indicesA
	indices.sort(key=lambda x:-x)#Sort in descending order
	for i in indices:
		ability=ability[:i]+'__'+ability[i:]
	return ability+'\n'

async def printAbilityTalents(message,abilities,talents,hotkey,hero):
	#Get ability name from hotkey
	abilityName=printAbility(abilities,hotkey).split('] ')[1].split(':')[0]
	output='\n'.join(ability for ability in abilities if abilityName in ability)

	#Search in talents for that ability
	output2=''
	levelTiers=[0,1,2,3,4,5,6]
	if hero=='Varian':
		del levelTiers[1]
	elif hero in ['Tracer','Deathwing']:
		pass
	else:
		del levelTiers[3]
	for i in levelTiers:
		talentTier=talents[i]
		for talent in talentTier:
			if abilityName in talent:
				output2+='\n'+talent

	if output2:
		output+=output2
	await printLarge(message.channel,output)

async def printSearch(abilities, talents, name, hero, deep=False):#Prints abilities and talents with substring
	name=abilityAliases(hero,name)
	name=name.replace('{','[').replace('}',']')#Search hotkeys/talent tiers
	if not name:
		return
	if '--' in name:
		[name,exclude]=name.split('--')
	else:
		exclude='this string is not in any abilities or talents'
	namelist=name.split('&')
	output=''
	for ability in abilities:
		if sum([1 for i in namelist if deepAndShallowSearchFoundBool(ability,i,deep)])==len(namelist) and exclude not in ability.lower():
			output+=await addUnderscoresAndNewline(namelist,ability)
	levelTiers=[0,1,2,3,4,5,6]
	if hero=='Varian':
		del levelTiers[1]
	elif hero in ['Tracer','Deathwing']:
		pass
	else:
		del levelTiers[3]
	for i in levelTiers:
		talentTier=talents[i]
		for talent in talentTier:
			if sum([1 for i in namelist if deepAndShallowSearchFoundBool(talent,i,deep)])==len(namelist) and exclude not in talent.lower():
				output+=await addUnderscoresAndNewline(namelist,talent)
	return output

async def printLarge(channel,inputstring,separator='\n'):#Get long string. Print lines out in 2000 character chunks
	strings=[i+separator for i in inputstring.split(separator)]
	
	output=strings.pop(0)
	i=0
	j=0
	while strings:
		if i==4:#Don't make a long call in #probius hog all the bandwidth
			i=0
			await asyncio.sleep(5)
		if len(output)+len(strings[0])<2000:
			output+=strings.pop(0)
		else:
			i+=1
			if j==0:
				firstMessage=await channel.send(output)
				j=1
			else:
				await channel.send(output)
			output=strings.pop(0)
	if j==0:
		firstMessage=await channel.send(output)
	else:
		await channel.send(output)
	return firstMessage

async def printAll(client,message,keyword, deep=False, heroList=getHeroes()):#When someone calls [all/keyword]
	toPrint=''
	for hero in heroList:
		(abilities,talents)=client.heroPages[hero]
		output=await printSearch(abilities,talents,keyword,hero,deep)
		if output=='':
			continue
		toPrint+='`'+hero.replace('_',' ')+':` '+output
	if toPrint=='':
		return
	if len(toPrint)>2000 and message.channel.guild.name in client.botChannels:#If the results is over one message, it gets dumped in specified bot channel
		channel=message.channel.guild.get_channel(client.botChannels[message.channel.guild.name])
		if channel==message.channel:#Already in #probius
			await printLarge(channel,toPrint)
		else:#Guild has a botchannel, the message was posted outside it
			introText=message.author.mention+'\n'+'Back to discussion: '+message.jump_url+'\n'
			toPrint=introText+toPrint
			redirectMessage=await message.channel.send('Sending large message in '+channel.mention+'...')
			firstMessage=await printLarge(channel,toPrint)
			await redirectMessage.edit(content=redirectMessage.content+'\n'+firstMessage.jump_url)
	else:#No bot channel
		await printLarge(message.channel,toPrint)

if __name__ == '__main__':
	from heroPage import heroAbilitiesAndTalents

	output=[]
	for hero in getHeroes():
		[abilities,talents]=heroAbilitiesAndTalents(hero)
		abilities=extraD(abilities,hero)
		for ability in abilities:
			if 'Quest' in ability:
				output.append(ability.split(':** ')[0])
	for i in output:
		print(i)

async def printEverything(client,message,abilities,talents):
	output=message.author.mention+'\n'+'\n'.join(abilities)+'\n'
	output+='\n'.join(talent for tier in talents for talent in tier)
	try:
		outputChannel=client.botChannels[message.channel.guild.name] 
	except:
		outputChannel=message.channel
	await printLarge(outputChannel,output)
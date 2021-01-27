#****************************************************************************
#Copyright (c) 2012 Antoine Godin
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#****************************************************************************

library(network)
library(plotrix)

fileName <- "../Bibliografia_Dissertacao/Bibliografia_Dissertacao.bib"

extractData<-function(text){
	index1=regexpr("\\{",text)+1
	indexes2=gregexpr("}",text)
	index2=indexes2[[1]][length(indexes2[[1]])]-1
	return(substring(text,index1,index2))
}

trimWSList<-function(listName){
	listName =list(gsub("^+[[:space:]]","", listName[[1]]))
	listName = list(gsub("[[:space:]]+$","", listName[[1]]))
	return(listName)
}

analyzeBibFile<-function(fileName,export=F){
	network=createAuthorNetwork(fileName,export=export)
	print("Do you want to see a time line for the whole network? [Yes]/No")
	ans = scan(what=character(),nlines=1,quiet=TRUE)
	while(length(ans)==0||ans=="Yes"){
		print("What characteristic do you want to see?")
		ans = scan(what=character(),nlines=1,quiet=TRUE)
		x11()
		a=createTimeLine(fileName,ans,allValues=TRUE,export=export)
		print("Do you want to see another time line for the whole network? [Yes]/No")
		ans = scan(what=character(),nlines=1,quiet=TRUE)
	}
	print("Do you want to analyse a shorter network? [Yes]/No")	
	ans = scan(what=character(),nlines=1,quiet=TRUE)
	while(length(ans)==0||ans=="Yes"){
		print("What is the name of one of the authors of the network?")
	 	auth = scan(what=character(),nlines=1,quiet=TRUE)
		print("What characteristic do you want to see?")
	 	param = scan(what=character(),nlines=1,quiet=TRUE)
	 	x11()
	 	a=createTimeLineByNetwork(fileName,auth,param,allValues=TRUE,plotNetwork=TRUE,export=export)
	 	print("Do you want to analyse another shorter network? [Yes]/No")
		ans = scan(what=character(),nlines=1,quiet=TRUE)
	}
}

createReferences<-function(fileName){
	bibFile=file(fileName)
	bibText=readLines(bibFile, n=-1)
	close(bibFile)
	counterEntries=0
	entries=c()
	comments=FALSE
	for (i in 1:length(bibText)){
		lineText=bibText[i]
		if (grepl("@",lineText)>0){
			if(counterEntries>0){
				entry=list(author=authors,methodology=methodologies,sector=sectors,asset=assets,characteristic=characteristics,year=year,title=title)
				if(counterEntries==1){entries=list(entry)}#If this is the first entry
				else{entries=append(entries,list(entry))}
				if(grepl("comment",lineText)){comments=TRUE}
			}
			counterEntries=counterEntries+1
			authors=NA
			methodologies=NA
			sectors=NA
			assets=NA
			characteristics=NA
			year=NA
			title=NA
		}
		if (pmatch("\tAuthor",lineText,nomatch=0)==1){
			authorsText=extractData(lineText)
			authorsList=trimWSList(strsplit(authorsText,"\ and\ "))[[1]]
			names=c()
			lastnames=c()
			for(j in 1:length(authorsList)){
				if(length(grep(",",authorsList[j]))==0){
					#format is name lastname
					authorNS=trimWSList(strsplit(authorsList[j],"[[:space:]]"))[[1]]
					if(length(authorNS)>2){
						lNS=length(authorNS)
						names=c(names,sub(",","",toString(authorNS[1:lNS-1],collapse = " ")))
						lastnames=c(lastnames,authorNS[lNS])
					}else if(length(authorNS)==2){
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[2])
					}else{
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[1])
					}				
				}else{
					#format is lastname, name
					authorNS=trimWSList(strsplit(authorsList[j],","))[[1]]
					names=c(names,authorNS[2])
					lastnames=c(lastnames,authorNS[1])
				}
			}
			authors=data.frame(name=names,lastname=lastnames)
		}
		else if(pmatch("\tKeywords",lineText,nomatch=0)==1){
			keywordText=extractData(lineText)
			keywords=trimWSList(strsplit(keywordText,"[,;]"))[[1]]
		}
		else if(pmatch("\tMethodology",lineText,nomatch=0)==1){
			methodologyText=extractData(lineText)
			methodologies=trimWSList(strsplit(methodologyText,"[,;]"))[[1]]
		}
		else if(pmatch("\tSectors",lineText,nomatch=0)==1){
			sectorText=extractData(lineText)
			sectors=trimWSList(strsplit(sectorText,"[,;]"))[[1]]
		}
		else if(pmatch("\tAssets",lineText,nomatch=0)==1){
			assetText=extractData(lineText)
			sectors=trimWSList(strsplit(assetText,"[,;]"))[[1]]
		}
		else if(pmatch("\tCharacteristics",lineText,nomatch=0)==1){
			characteristicText=extractData(lineText)
			characteristic=trimWSList(strsplit(characteristicText,"[,;]"))[[1]]
		}
		else if(pmatch("\tYear",lineText,nomatch=0)==1){
			year=extractData(lineText)
			if(suppressWarnings(!is.na(as.numeric(year)))){year=as.numeric(year)}
			else{year=as.numeric(substr(year,1,4))}
		}
		else if(pmatch("\tTitle",lineText,nomatch=0)==1){
			title=extractData(lineText)
		}
		if(i==length(bibText)&&comments==FALSE){
			entry=list(author=authors,methodology=methodologies,sector=sectors,asset=assets,characteristic=characteristics,year=year,title=title)
			entries=append(entries,list(entry))
		}
	}
	return(entries)
}

addCollaboration<-function(matrix,index1,index2,nAuths){
	incr=1/(nAuths-1)
	matrix[index1,index2]=matrix[index1,index2]+incr
	matrix[index2,index1]=matrix[index2,index1]+incr
	return(matrix)
}

addAuthor<-function(matrix){
	
	#just adding a new author
	matrix=cbind(matrix,0)
	matrix=rbind(matrix,0)
	return(matrix)
}

checkAuthors<-function(networkMatrix,names,lastnames,authorsName,authorsLastname){
	lAuths=length(lastnames)
	for(j in 1:lAuths){
		if(is.null(authorsLastname)){
			networkMatrix=matrix(0,1,1)
			authorsName=c(authorsName,names[j])
			authorsLastname=c(authorsLastname,lastnames[j])
		}
		indexAuth=pmatch(lastnames[j],authorsLastname,nomatch=0)
		if(indexAuth>0){
			#author maybe already present
			#treating the different name structure
			if(grepl("[[:space:]]",names[j])){
				#composed first name
				if(grepl("[[:space:]]",authorsName[indexAuth])){
					namesAuth=trimWSList(strsplit(names[j],"[[:space:]]"))[[1]]
					namesList=trimWSList(strsplit(authorsName[indexAuth],"[[:space:]]"))[[1]]
					if(length(namesAuth)==length(namesList)){
						#for now just check that the first letters coincide
						ok=TRUE
						for(k in 1:length(namesList)){
							if(substr(namesList,1,1)!=substr(namesAuth,1,1)){ok=FALSE}
						}
						if(!ok){
							#not the same names
							networkMatrix=addAuthor(networkMatrix)
							authorsName=c(authorsName,names[j])
							authorsLastname=c(authorsLastname,lastnames[j])
						}
					}else{
						#not the same length
						networkMatrix=addAuthor(networkMatrix)
						authorsName=c(authorsName,names[j])
						authorsLastname=c(authorsLastname,lastnames[j])
					}
				}else{
					#not the same author thus add the author
					networkMatrix=addAuthor(networkMatrix)
					authorsName=c(authorsName,names[j])
					authorsLastname=c(authorsLastname,lastnames[j])
				}
			}
			else{
				#Simple name
				nameAuth=names[j]
				nameList=authorsName[indexAuth]	
				shortNA=NA
				shortNL=NA
				longNA=NA
				longNL=NA
				if(nchar(nameAuth)>2){
					shortNA=paste(substr(nameAuth,1,1),".",sep="")
					longNA=nameAuth
				}else{
					if(nchar(nameAuth)==1){
						shortNA=paste(nameAuth,".",sep="")
						longNA= shortNA
					}
					else{
						shortNA=nameAuth
						longNA=nameAuth
					}
				}
				if(nchar(nameList)>2){
					shortNL=paste(substr(nameList,1,1),".",sep="")
					longNL=nameList
				}else{
					if(nchar(nameList)==1){
						shortNL=paste(nameList,".",sep="")
						longNL= shortNL
					}
					else{
						shortNL=nameList
						longNL=nameList
					}
				}
				if(longNA!=longNL&shortNA!=shortNL){
					#If none of the names match
					networkMatrix=addAuthor(networkMatrix)
					authorsName=c(authorsName,names[j])
					authorsLastname=c(authorsLastname,lastnames[j])
				}
			}
		}
		else{
			#add the author
			networkMatrix=addAuthor(networkMatrix)
			authorsLastname=c(authorsLastname,lastnames[j])
			authorsName=c(authorsName,names[j])
		}
	}
	return(list(mat=networkMatrix,nam=authorsName,sur=authorsLastname))
}

createAuthorNetwork<-function(fileName,minPubl=4,plotNetwork=TRUE,export=F){
	bibFile=file(fileName)
	bibText=readLines(bibFile, n=-1)
	close(bibFile)
	authorsName=c()
	authorsLastname=c()
	networkMatrix=matrix(data=0)
	comments=FALSE
	counterEntries=0
	for (i in 1:length(bibText)){
		lineText=bibText[i]
		if (grepl("@",lineText)>0){
			if(counterEntries>0){
				#first add the authors to the authorlist
				res=checkAuthors(networkMatrix,names,lastnames,authorsName,authorsLastname)
				authorsName=res$nam
				authorsLastname=res$sur
				networkMatrix=res$mat
				#then update the network matrix
				lAuths=length(lastnames)
				if(lAuths>1){
					for(j in 1:lAuths){
						indexAuth=pmatch(lastnames[j],authorsLastname)
						for(k in j+1:lAuths){
							indexAuth2=pmatch(lastnames[k],authorsLastname)
							networkMatrix= addCollaboration(networkMatrix,indexAuth,indexAuth2,lAuths)
						}
					}
				}else{
					indexAuth=pmatch(lastnames[1],authorsLastname)
					networkMatrix= addCollaboration(networkMatrix,indexAuth, indexAuth,3)
				}
				if(grepl("comment",lineText)){comments=TRUE}
			}
			counterEntries=counterEntries+1
			#clean the local variables
			names=NA
			lastnames=NA
		}
		if (pmatch("\tAuthor",lineText,nomatch=0)==1){
			authorsText=extractData(lineText)
			authorsList=trimWSList(strsplit(authorsText,"\ and\ "))[[1]]
			names=c()
			lastnames=c()
			for(j in 1:length(authorsList)){
				if(length(grep(",",authorsList[j]))==0){
					#format is name lastname
					authorNS=trimWSList(strsplit(authorsList[j],"[[:space:]]"))[[1]]
					if(length(authorNS)>2){
						lNS=length(authorNS)
						names=c(names,sub(",","",toString(authorNS[1:lNS-1],collapse = " ")))
						lastnames=c(lastnames,authorNS[lNS])
					}else if(length(authorNS)==2){
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[2])
					}else{
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[1])
					}				
				}else{
					#format is lastname, name
					authorNS=trimWSList(strsplit(authorsList[j],","))[[1]]
					names=c(names,authorNS[2])
					lastnames=c(lastnames,authorNS[1])
				}
			}
		}
		if(i==length(bibText)&&comments==FALSE){
			#first add the authors to the authorlist
			res=checkAuthors(networkMatrix,names,lastnames,authorsName,authorsLastname)
			authorsName=res$nam
			authorsLastname=res$sur
			networkMatrix=res$mat
			#then update the network matrix
			lAuths=length(lastnames)
			if(lAuths>1){
				for(j in 1:lAuths){
					indexAuth=pmatch(lastnames[j],authorsLastname)
					for(k in j+1:lAuths){
						indexAuth2=pmatch(lastnames[k],authorsLastname)
						networkMatrix= addCollaboration(networkMatrix,indexAuth,indexAuth2,lAuths)
					}
				}
			}else{
				indexAuth=pmatch(lastnames[1],authorsLastname)
				networkMatrix= addCollaboration(networkMatrix,indexAuth, indexAuth,3)
			}
		}
	}
	rownames(networkMatrix)=authorsLastname
	colnames(networkMatrix)=authorsLastname
	net<-network(networkMatrix,loops=TRUE,directed=FALSE)
	paperCollaborations=c()
	for(i in 1:length(authorsLastname)){
		paperCollaborations=c(paperCollaborations,sum(networkMatrix[i,]))
	}
	if(plotNetwork){
		plot(net,displaylabels=TRUE,label.pos=1,boxed.labels=FALSE,label.cex=0.001+(paperCollaborations>=minPubl),vertex.col=2+(paperCollaborations>=minPubl)#,main=paste("Network for",fileName)
		)
		if(export){
			dev.copy2eps(file=paste("Network",".ps",sep=""))
			dev.off()
		}
	}
	return(networkMatrix)
}

createTimeLine<-function(fileName,paramName,paramValues=c(),allValues=FALSE,export=F){
	bibFile=file(fileName)
	bibText=readLines(bibFile, n=-1)
	close(bibFile)
	counterEntries=0
	if(allValues){paramValues=c()}
	nValues=length(paramValues)
	paramList=vector("list",nValues)
	comments=FALSE
	for (i in 1:length(bibText)){
		lineText=bibText[i]
		if (grepl("@",lineText)>0){
			if(counterEntries>0){
				if(!is.na(params)&!is.na(year)){
				nOValues=length(params)
					for(j in 1:nOValues){
						if(allValues){
							if(pmatch(toupper(params[j]),paramValues,nomatch=0)==0){
								paramValues=c(paramValues,toupper(params[j]))
								nValues=length(paramValues)
								if(nValues==1){
									paramList=vector("list",nValues)
								}
								else{
									paramListbis=vector("list",nValues)
									for(k in 1:(nValues-1)){
										paramListbis[[k]]=paramList[[k]]
									}
									paramList=paramListbis
								}
							}
						}
						for(k in 1:nValues){
							if(toupper(params[j])==toupper(paramValues[k])){
								listOfDates=paramList[[k]]
								if(is.null(listOfDates)){
									listOfDates=c(year)
								}
								else{
									listOfDates=c(listOfDates,year)
								}
								paramList[[k]]=listOfDates
								k=nValues+1
							}
						}
					}
				}
				if(grepl("comment",lineText)){comments=TRUE}
			}
			counterEntries=counterEntries+1
			params=NA
			year=NA
		}
		if(pmatch(paste("\t",paramName,sep=""),lineText,nomatch=0)==1){
			paramText=extractData(lineText)
			params=trimWSList(strsplit(paramText,"[,;/\\]"))[[1]]
		}
		else if(pmatch("\tYear",lineText,nomatch=0)==1){
			year=extractData(lineText)
			if(suppressWarnings(!is.na(as.numeric(substr(year,1,4))))){year=as.numeric(substr(year,1,4))}
			else{year=NA}
		}
		if(i==length(bibText)&&comments==FALSE){
			if(!is.na(params)&!is.na(year)){
				nOValues=length(params)
				for(j in 1:nOValues){
					if(allValues){
						if(pmatch(toupper(params[j]),paramValues,nomatch=0)==0){
							paramValues=c(paramValues,toupper(params[j]))
							nValues=length(paramValues)
							paramListbis=vector("list",nValues)
							for(k in 1:nValues-1){
								paramListbis[[k]]=paramList[[k]]
							}
							paramList=paramListbis
						}
					}
					for(k in 1:nValues){
						if(toupper(params[j])==toupper(paramValues[k])){
							listOfDates=paramList[[k]]
							if(is.null(listOfDates)){
								listOfDates=c(year)
							}
							else{
								listOfDates=c(listOfDates,year)
							}
							paramList[[k]]=listOfDates
							k=nValues+1
						}
					}
				}
			}
		}
	}
	Ymd.format="%Y/%m/%d"
	allLabels=c()
	allStarts=c()
	allEnds=c()
	allDensities=c()
	for(i in 1:nValues){
		listOfDates=paramList[[i]]
		if(!is.null(listOfDates)){
			listOfDates=sort(listOfDates)
			dates=c()
			starts=c()
			ends=c()
			density=c()
			labels=c()
			lDates=length(listOfDates)
			for(j in 1:lDates){
				index=pmatch(listOfDates[j],dates,nomatch=0)
				if(index==0){
					dates=c(dates,listOfDates[j])
					starts=c(starts,paste(toString(listOfDates[j]),"/01/01",sep=""))
					ends=c(ends,paste(toString(listOfDates[j]),"/12/31",sep=""))
					labels=c(labels,paramValues[i])
					density=c(density,1)
				}else{
					density[index]=density[index]+1
				}
			}
		}
		allLabels=c(allLabels,labels)
		allStarts=c(allStarts,starts)
		allEnds=c(allEnds,ends)
		allDensities=c(allDensities,density)
		paramList[[i]]=data.frame(dates=dates,density=density,starts=starts,ends=ends,labels=labels)
	}
	gantt.info<-list(labels=allLabels, starts=as.POSIXct(strptime(allStarts,format=Ymd.format)), ends=as.POSIXct(strptime(allEnds,format=Ymd.format)),priorities=allDensities)
	gantt.chart(gantt.info
	#,main=paste("Timeline for",paramName)
	,hgrid=TRUE
	,taskcolors=1+allDensities
	,priority.legend=TRUE)
	if(export){
			dev.copy2eps(file=paste("TimeLine",paramName,".ps",sep=""))
			dev.off()
	}
	return(paramList)
}

createTimeLineByNetwork<-function(fileName,networkName,paramName,paramValues=c(),allValues=FALSE,plotNetwork=FALSE,minPubl=0,export=F){
	matrix=createAuthorNetwork(fileName,plotNetwork=FALSE,export=export)
	authorNames=c(networkName)
	nNames=length(authorNames)
	allNames=rownames(matrix)
	i=1
	while(i<=nNames){
		tempName=authorNames[i]
		row=matrix[tempName,]
		for(j in 1:length(row)){
			if(row[j]>0){
				if(pmatch(allNames[j],authorNames,nomatch=0)==0){
					authorNames=c(authorNames, allNames[j])
					nNames=length(authorNames)
				}
			}
		}
		i=i+1
	}
	bibFile=file(fileName)
	bibText=readLines(bibFile, n=-1)
	close(bibFile)
	counterEntries=0
	if(allValues){paramValues=c()}
	nValues=length(paramValues)
	print(nNames)
	paramList=vector("list",nValues)
	comments=FALSE
	for (i in 1:length(bibText)){
		lineText=bibText[i]
		if (grepl("@",lineText)>0){
			if(counterEntries>0){
				if(!is.na(params)&!is.na(year)&pmatch(lastnames[1],authorNames,nomatch=0)>0){
					nOValues=length(params)
					for(j in 1:nOValues){
						if(allValues){
							if(pmatch(toupper(params[j]),paramValues,nomatch=0)==0){
								paramValues=c(paramValues,toupper(params[j]))
								nValues=length(paramValues)
								if(nValues==1){
									paramList=vector("list",nValues)
								}
								else{
									paramListbis=vector("list",nValues)
									for(k in 1:(nValues-1)){
										paramListbis[[k]]=paramList[[k]]
									}
									paramList=paramListbis
								}
							}
						}
						for(k in 1:nValues){
							if(toupper(params[j])==toupper(paramValues[k])){
								listOfDates=paramList[[k]]
								if(is.null(listOfDates)){
									listOfDates=c(year)
								}
								else{
									listOfDates=c(listOfDates,year)
								}
								paramList[[k]]=listOfDates
								k=nValues+1
							}
						}
					}
				}
				if(grepl("comment",lineText)){comments=TRUE}
			}
			counterEntries=counterEntries+1
			params=NA
			year=NA
			names=NA
			lastnames=NA
		}
		if(pmatch(paste("\t",paramName,sep=""),lineText,nomatch=0)==1){
			paramText=extractData(lineText)
			params=trimWSList(strsplit(paramText,"[,;/\\]"))[[1]]
		}
		else if (pmatch("\tAuthor",lineText,nomatch=0)==1){
			authorsText=extractData(lineText)
			authorsList=trimWSList(strsplit(authorsText,"\ and\ "))[[1]]
			names=c()
			lastnames=c()
			for(j in 1:length(authorsList)){
				if(length(grep(",",authorsList[j]))==0){
					#format is name lastname
					authorNS=trimWSList(strsplit(authorsList[j],"[[:space:]]"))[[1]]
					if(length(authorNS)>2){
						lNS=length(authorNS)
						names=c(names,sub(",","",toString(authorNS[1:lNS-1],collapse = " ")))
						lastnames=c(lastnames,authorNS[lNS])
					}else if(length(authorNS)==2){
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[2])
					}else{
						names=c(names,authorNS[1])
						lastnames=c(lastnames,authorNS[1])
					}				
				}else{
					#format is lastname, name
					authorNS=trimWSList(strsplit(authorsList[j],","))[[1]]
					names=c(names,authorNS[2])
					lastnames=c(lastnames,authorNS[1])
				}
			}
		}
		else if(pmatch("\tYear",lineText,nomatch=0)==1){
			year=extractData(lineText)
			if(suppressWarnings(!is.na(as.numeric(substr(year,1,4))))){year=as.numeric(substr(year,1,4))}
			else{year=NA}
		}
		if(i==length(bibText)&&comments==FALSE){
			if(!is.na(params)&!is.na(year)){
				nOValues=length(params)
				for(j in 1:nOValues){
					if(allValues){
						if(pmatch(toupper(params[j]),paramValues,nomatch=0)==0){
							paramValues=c(paramValues,toupper(params[j]))
							nValues=length(paramValues)
							paramListbis=vector("list",nValues)
							for(k in 1:nValues-1){
								paramListbis[[k]]=paramList[[k]]
							}
							paramList=paramListbis
						}
					}
					for(k in 1:nValues){
						if(toupper(params[j])==toupper(paramValues[k])){
							listOfDates=paramList[[k]]
							if(is.null(listOfDates)){
								listOfDates=c(year)
							}
							else{
								listOfDates=c(listOfDates,year)
							}
							paramList[[k]]=listOfDates
							k=nValues+1
						}
					}
				}
			}
		}
	}
	Ymd.format="%Y/%m/%d"
	allLabels=c()
	allStarts=c()
	allEnds=c()
	allDensities=c()
	for(i in 1:nValues){
		listOfDates=paramList[[i]]
		if(!is.null(listOfDates)){
			listOfDates=sort(listOfDates)
			dates=c()
			starts=c()
			ends=c()
			density=c()
			labels=c()
			lDates=length(listOfDates)
			for(j in 1:lDates){
				index=pmatch(listOfDates[j],dates,nomatch=0)
				if(index==0){
					dates=c(dates,listOfDates[j])
					starts=c(starts,paste(toString(listOfDates[j]),"/01/01",sep=""))
					ends=c(ends,paste(toString(listOfDates[j]),"/12/31",sep=""))
					labels=c(labels,paramValues[i])
					density=c(density,1)
				}else{
					density[index]=density[index]+1
				}
			}
		}
		allLabels=c(allLabels,labels)
		allStarts=c(allStarts,starts)
		allEnds=c(allEnds,ends)
		allDensities=c(allDensities,density)
		paramList[[i]]=data.frame(dates=dates,density=density,starts=starts,ends=ends,labels=labels)
	}
	gantt.info<-list(labels=allLabels, starts=as.POSIXct(strptime(allStarts,format=Ymd.format)), ends=as.POSIXct(strptime(allEnds,format=Ymd.format)),priorities=allDensities)
	
	x11(width=9,height=9)
	gantt.chart(gantt.info
	#,main=paste("Timeline for the network",networkName,"for",paramName)
	,hgrid=TRUE
	,taskcolors=colors()[253-90*(allDensities)/max(allDensities)]#This is for black and white colouring
#	,vgrid.format='%Y'
	,vgridpos=as.POSIXct(strptime(paste(as.character(format(strptime(min(allStarts),format=Ymd.format),format='%Y'):format(strptime(max(allStarts),format=Ymd.format),format='%Y')),"/01/01",sep=""),format=Ymd.format))
	,vgridlab=as.character(format(strptime(min(allStarts),format=Ymd.format),format='%Y'):format(strptime(max(allStarts),format=Ymd.format),format='%Y'))
	,priority.legend=FALSE)
	if(export){
		dev.copy2eps(file=paste("TimeLine_",networkName,"_",paramName,".ps",sep=""))
		dev.off()
	}
	networkMatrix=matrix[authorNames,authorNames]
	net<-network(networkMatrix,loops=TRUE,directed=FALSE)
	paperCollaborations=c()
	for(i in 1:length(authorNames)){
		paperCollaborations=c(paperCollaborations,sum(networkMatrix[i,]))
	}
	if(plotNetwork){
		plot(net,main=paste("Subnetwork for",networkName),displaylabels=TRUE,label.pos=1,boxed.labels=FALSE,label.cex=0.001+(paperCollaborations>minPubl),vertex.col=2+(paperCollaborations>minPubl))
		if(export){
			dev.copy2eps(file=paste("Subnetwork",networkName,".ps",sep=""))
			dev.off()
		}
	}
	return(paramList)
}

createAuthorSubnetwork<-function(fileName,networkName,plotNetwork=TRUE,minPubl=0,export=F){
	matrix=createAuthorNetwork(fileName,plotNetwork=FALSE,export=export)
	authorNames=c(networkName)
	nNames=length(authorNames)
	allNames=rownames(matrix)
	i=1
	while(i<=nNames){
		tempName=authorNames[i]
		row=matrix[tempName,]
		for(j in 1:length(row)){
			if(row[j]>0){
				if(pmatch(allNames[j],authorNames,nomatch=0)==0){
					authorNames=c(authorNames, allNames[j])
					nNames=length(authorNames)
				}
			}
		}
		i=i+1
	}
	networkMatrix=matrix[authorNames,authorNames]
	net<-network(networkMatrix,loops=TRUE,directed=FALSE)
	paperCollaborations=c()
	for(i in 1:length(authorNames)){
		paperCollaborations=c(paperCollaborations,sum(networkMatrix[i,]))
	}
	if(plotNetwork){
		x11()
		plot(net,main=paste("Subnetwork for",networkName),displaylabels=TRUE,label.pos=1,boxed.labels=FALSE,label.cex=0.001+(paperCollaborations>minPubl),vertex.col=2+(paperCollaborations>minPubl))
	}
	return(paramList)
}

analyzeBibFile(fileName = fileName)


const _baseurl = window.location.origin;
const _enhance = [0,1,2,3];

const RANK_NONE = 0  ;
const RANK_OFF = 1   ;
const RANK_BAD = 2   ;
const RANK_OK = 3    ;
const RANK_GOOD = 4  ;
const RANK_BEST = 5  ;



var _border = [];

_border[RANK_NONE]="border-white"      ;
_border[RANK_OFF ]="border-white"      ;
_border[RANK_BAD ]="border-secondary"  ;
_border[RANK_OK  ]="border-primary"    ;
_border[RANK_GOOD]="border-warning"    ;
_border[RANK_BEST]="border-success"	   ;		


const _mon = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']	
				

function bmpurl(e,enhance_mode)
{
	return _baseurl+"/bmp/"+e.id.toString()+"/"+e.mon.toString()+"/"+e.day.toString()+"/"+enhance_mode.toString();
	
}

function uniqueid(id,mon,day,enhance_mode)
{
	return "img_"+id.toString()+"_"+mon.toString()+"_"+day.toString()+"_"+enhance_mode.toString()
	
}

function imgset(tagid,dbid,mon,day,enhance_mode,rank)
{
	console.log("imgset",tagid,dbid,mon,day,"->",enhance_mode,rank);
	
	const url = _baseurl+"/set/"+dbid.toString()+"/"+mon.toString()+"/"+day.toString()+"/"+enhance_mode.toString()+"/"+rank.toString();

	$.getJSON( url, function( data ) 
	{
		console.log("done");
		
	});
	
}


function imgclick(tagid,dbid,mon,day,enhance_mode)
{
	console.log("imgclick",tagid,dbid,mon,day,enhance_mode);
	
	if ($('#'+tagid).hasClass( _border[RANK_OK] ))	
	{	$('#'+tagid).removeClass(_border[RANK_OK]);
		$('#'+tagid).addClass(_border[RANK_GOOD]);
		imgset(tagid,dbid,mon,day,enhance_mode,RANK_GOOD);
		return;
	}

	if ($('#'+tagid).hasClass( _border[RANK_GOOD] ))	
	{	$('#'+tagid).removeClass(_border[RANK_GOOD]);
		$('#'+tagid).addClass(_border[RANK_BEST]);
		imgset(tagid,dbid,mon,day,enhance_mode,RANK_BEST);
		return;
	}

	if ($('#'+tagid).hasClass( _border[RANK_BEST] ))	
	{	$('#'+tagid).removeClass(_border[RANK_BEST]);
		$('#'+tagid).addClass(_border[RANK_OFF]);
		imgset(tagid,dbid,mon,day,enhance_mode,RANK_OFF);
		return;
	}

	
	for (enh of _enhance) 
	{
		const imgid = uniqueid(dbid,mon,day,enh);
		$('#'+imgid).removeClass();
		if (enh!=enhance_mode)
		{
			$('#'+imgid).addClass("border");
			$('#'+imgid).addClass(_border[RANK_OFF]);		
		}
	}	

	$('#'+tagid).addClass("border");
	$('#'+tagid).addClass(_border[RANK_OK]);
	imgset(tagid,dbid,mon,day,enhance_mode,RANK_OK);
	
}


function main(dbid,mon,day,divid)
{
	console.log(dbid,mon,day);
	
	
	const url = _baseurl+"/dat/*/"+mon.toString()+"/"+day.toString();
	
	$('#'+divid).html('Loading... '+url );


	var text = [];
	
	var html_r = "";
	var html_l = "";
	var html_c = "";
	
	{
		let d = day-1;
		let m = mon;
		if (d==0)
		{	d=31
			m-=1;
			if (m==0)
				m=12;
		}
		let u = _baseurl+"/tab/*/"+m.toString()+"/"+d.toString();
		html_l = '<a href="'+u+'">&lt;&lt;</a>';
	
	}
	html_c = '&nbsp;&nbsp;&nbsp;'+day.toString()+' '+_mon[mon-1]+'&nbsp;&nbsp;&nbsp;';
	{
		let d = day+1;
		let m = mon;
		if (d==32)
		{	d=1
			m+=1;
			if (m==13)
				m=1;
		}
		let u = _baseurl+"/tab/*/"+m.toString()+"/"+d.toString();
		html_r ='<a href="'+u+'">&gt;&gt;</a>';
		
	}

	text.push('<h1>');
	text.push(html_l);
	text.push(html_c);
	text.push(html_r);
	text.push('</h1>');

	text.push('<p>');
	for(var i=1;i<13;i++)
		if (i==mon)
		{
			text.push(_mon[i-1]+' ');			
		} else
		{
			let u = _baseurl+"/tab/*/"+i.toString()+"/1";
			text.push('<a href="'+u+'">'+_mon[i-1]+'</a> ');
		}

	text.push('</p>');
	text.push('<p>');
	for(var i=1;i<32;i++)
		if (i==day)
		{
			text.push(i.toString()+' ');			
		} else
		{
			let u = _baseurl+"/tab/*/"+mon.toString()+"/"+i.toString();
			text.push('<a href="'+u+'">'+i.toString()+'</a> ');
		}
	text.push('</p>');
		
	$.getJSON( url, function( data ) 
	{
		//console.log(data);
		

		for (e of data) 
		{
			//console.log(e);
			text.push('<div>');
			for (enh of _enhance) 
			{
				const alttxt = '['+e.id.toString()+']  '+e.day.toString()+' '+_mon[mon-1]+' ('+enh.toString()+')';
				const imgid = uniqueid(e.id,e.mon,e.day,enh);
				const imgurl = bmpurl(e,enh);
				text.push('<img id="'+imgid+'" src="'+imgurl+'" alt="'+alttxt+'" ');
				text.push('onclick="imgclick(\''+imgid+'\',\''+e.id.toString()+'\','+e.mon.toString()+','+e.day.toString()+','+enh.toString()+');" '); 
				text.push('class="border '+_border[enh==e.enhance ? e.rank : RANK_NONE ]+'" ');

					
				text.push('>');
			}
			text.push('</div>');							

				
		}

		text.push('<h3>');
		text.push(html_l);
		text.push(html_c);
		text.push(html_r);
		text.push('</h3>');

		$('#'+divid).html(text.join(''));

		
	});


}

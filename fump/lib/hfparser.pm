#!/usr/bin/perl
#################################################################
#FILE: hfparser.pm
#HTML FORM PARSING MODULE
#################################################################
package hfparser;
use strict;
use dparser;
use vars qw($q @ISA $def_class $def_over_class $def_error_class $VERSION);
push(@ISA,"dparser");
#@EXPORT=qw($q);

$VERSION='1.6';
$def_class="INPUTmy";
$def_over_class="INPUTmyACT";
$def_error_class="INPUTmyERR";
$hfparser::errorheader="Error(s) detected" unless $hfparser::errorheader;
#############################################
sub setCGI{
	my $CGI=shift;
	$q=$CGI;
	eval('use CGI; $q=new CGI') unless ($q);
}
sub _set_defaults_errors{
	my $self=shift;
	$self->{ERROR_HEADER}="<DIV class=\"ERROR_HEADER\">$hfparser::errorheader</DIV>" unless ($self->{ERROR_HEADER}) ;
	$self->{ERROR_AFTER_TEMPL}="<BR><SPAN class=\"ERROR_ELEMENT\">###ERR###</SPAN>" unless ($self->{ERROR_AFTER_TEMPL});
	$self->{ERROR_AFTER_TEMPL_INPLACE}="<SPAN class=\"ERROR_ELEMENT\">###ERR###</SPAN>" unless ($self->{ERROR_AFTER_TEMPL_INPLACE});	
	if ($self->{ERROR_AFTER_INPUT} eq '0'){
		$self->{ERROR_TEMPL_BEFOR}="<FONT color=red><UL>" unless ($self->{ERROR_TEMPL_BEFOR});
		$self->{ERROR_TEMPL}="<LI>###ERR###</LI>" unless ($self->{ERROR_TEMPL});
		$self->{ERROR_TEMPL_AFTER}="</UL></FONT>" unless ($self->{ERROR_TEMPL_AFTER});
	}

}
######
sub _crosshesh{
	my $self = shift;
	my $first_ref=shift;
	my $default_ref=shift;
	$first_ref={} unless $first_ref;
	$default_ref={} unless $default_ref;
	my %first=%{$first_ref};
	my %default=%{$default_ref};
	foreach my $key(keys %default){
		$first{$key}=$default{$key} unless exists($first{$key});
	}

	return  %first;
}

sub set_default_input{
	$_[0]->{INPUT_DEF}{$_[1]}{$_[2]}=$_[3];
}
######
sub _set_defaults{
	my $self=shift;
	$self->add_parsing(\&ParseString);
	$self->add_func('{error}',\&printerror,$self);
	###DEFAULTS FOR DATAPARSER
	$self->SUPER::_set_defaults();
	###DEFAULTS FOR FORMPARSER
	$self->{INPUT_DEF}{"text"}{"size"}=15;
	$self->{INPUT_DEF}{"text"}{"maxlength"}=80;
	$self->{INPUT_DEF}{"text"}{"class"}=$def_class;
	$self->{INPUT_DEF}{"text"}{"on_err_class"}=$def_error_class;
	$self->{INPUT_DEF}{"text"}{"onFocus"}="this.className ='$def_over_class' ;";
	$self->{INPUT_DEF}{"text"}{"onBlur"}=" this.className ='$def_class' ;";
	####Поля TEXTAREA
	$self->{INPUT_DEF}{"textarea"}{"rows"}=10;
	$self->{INPUT_DEF}{"textarea"}{"columns"}=40;
	$self->{INPUT_DEF}{"textarea"}{"class"}=$def_class;
	$self->{INPUT_DEF}{"textarea"}{"on_err_class"}=$def_error_class;
	$self->{INPUT_DEF}{"textarea"}{"onFocus"}="this.className ='$def_over_class' ;";
	$self->{INPUT_DEF}{"textarea"}{"onBlur"}=" this.className ='$def_class' ;";
	####Поля BUTTON
	$self->{INPUT_DEF}{"button"}{"value"}='Submit';
	$self->{INPUT_DEF}{"button"}{"type"}='submit';
	####Поля SELECT
	$self->{INPUT_DEF}{"select"}{"class"}=$def_class;
	if($ENV{'HTTP_USER_AGENT'}!~/opera/i){
		$self->{INPUT_DEF}{"select"}{"onFocus"}="this.className ='$def_over_class' ; ";
		$self->{INPUT_DEF}{"select"}{"onBlur"}=" this.className ='$def_class';";
	}
	$self->{INPUT_DEF}{"select"}{"on_err_class"}=$def_error_class;
	##Поля LIST
	$self->{INPUT_DEF}{"list"}{"onFocus"}="this.className ='$def_over_class';";
	$self->{INPUT_DEF}{"list"}{"onBlur"}=" this.className ='$def_class'; ";
	$self->{INPUT_DEF}{"list"}{"multiple"}="true";
	$self->{INPUT_DEF}{"list"}{"size"}=4;
	$self->{INPUT_DEF}{"list"}{"class"}=$def_class;
	##Поля CHECKBOX
	$self->{INPUT_DEF}{"check"}{"label"}=" ";
	##Поля RADIO
	$self->{INPUT_DEF}{"radio"}{"linebreak"}="true";
	###
	#
	$self->{ERROR_AFTER_INPUT}=1;
	$self->_set_defaults_errors;
}
######
sub printerror{
	my $self = shift;
	my $out;
	return unless $self->is_error;
#    return unless ($self->{ERROR});
	if ($self->{ERROR_AFTER_INPUT} eq '0'){
		$out.=$self->{ERROR_HEADER};
		#
		$out.=$self->{ERROR_TEMPL_BEFOR}."\n";
		my %error=%{$self->{ERROR}};
		foreach my $n (keys %error){
			my $templ=$self->{ERROR_TEMPL};
			$templ=~s/###ERR###/$self->{ERROR}{$n}/;
			$out.=$templ."\n" if ($self->{ERROR}{$n} ne ' ');
		}
		$out.=$self->{ERROR_TEMPL_AFTER}."\n";
	}else{
		#
		$out.=$self->{ERROR_HEADER};
	}
	return $out;
}
###########################
sub processTEXT{
	my $self = shift;
	my $type = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{text});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$out.=$q->textfield(\%params) if ($type eq 'text');
	$out.=$q->password_field(\%params) if ($type eq 'password');
	return $out;
}
###########################
sub processTEXTAREA{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{textarea});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$out.=$q->textarea(\%params);
	return $out;
}
########
sub processBUTTON{
	my $self = shift;
	my $type = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{button});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
#	$out.=$q->button(\%params);
	$out.=$q->submit(\%params) if ($type eq 'submit');
	$out.=$q->button(\%params) if ($type eq 'button');
	return $out;
}
###########################
sub processSELECT{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{select});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$out.=$q->popup_menu(\%params);
	return $out;
}
###########################
sub processCHECK{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{check});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	if (exists($self->{DEFAULT}{$name})){	
		$params{selected}='on' if ($self->{DEFAULT}{$name});
	}
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$out.=$q->checkbox(\%params);
	return $out;
}
###########################
sub processRADIOGROUP{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{radio});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$out.=$q->radio_group(\%params);
	return $out;
}
sub processRADIO{
	my $self = shift;
	my $name = shift;
	my $addparams=shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{radio});
	%params=$self->_crosshesh($addparams,\%params);
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$params{linebreak}=0;
	#$params{labels}={$params{value},""};
	$out.=$q->radio_group(\%params);
	#$out=~s/<BR>//g;
	return $out;
}
###########################
sub processLIST{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{list});
	my $errclass;
	####
	if ($params{on_err_class}){
		$errclass=$params{on_err_class};
		delete($params{on_err_class});
	}
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{class}=$errclass if $self->{ERROR}{$name};
	$params{name}=$name;
	$out.=$q->scrolling_list(\%params);
	return $out;
}
###########################
sub processHIDDEN{
	my $self = shift;
	my $name = shift;
	my $out;
	my %params=$self->_crosshesh($self->{INPUT}{$name},$self->{INPUT_DEF}{hidden});
	$params{default}=$self->{DEFAULT}{$name} if exists($self->{DEFAULT}{$name});
	$params{name}=$name;
	$out.=$q->hidden(\%params);
	$out=~s/\/>$/>/; 
	return $out;
}
##########
sub ProcessElement{
	my $self=shift;
	my $input=shift;
	$input=~s/^\{fm_//;
	my ($type,$name)=($input=~/^([^_]+)_(.*)\}$/);
	my $out;
	my $add_params={};
	if($name=~s/\((.+)\)//){
		my $add_str=$1;
		my @arr=($add_str=~/([^\s]+\s*=\s*[^\s]+)/g);
		foreach my $el(@arr){
			my($n,$v)=split(/\s*=\s*/,$el);
			$add_params->{$n}=$v;
		}
	}
	if($name=~s/##PAR##(.*)$//){
		my $add_values=$1;
		my @arr=split /##/,$add_values;
		map{ 
			if(/(.*?)=(.*)/){
				my $n=$1; 
				my $v=$2;
				$n=~s/\s//g;
				$add_params->{$n}=$v;				
			}
		}@arr;
	}
	$name=~s/\s+//g;
	unless($type eq 'radio'){
		$self->set_input($name, $add_params) if keys (%$add_params);
	}
	if ($type eq 'text' || $type eq 'password'){
		$out=$self->processTEXT($type,$name);
	}elsif($type eq 'textarea'){
		$out=$self->processTEXTAREA($name);
	}elsif($type eq 'select'){
		$out=$self->processSELECT($name);
	}elsif($type eq 'hidden'){
		$out=$self->processHIDDEN($name);
	}elsif($type eq 'list'){
		$out=$self->processLIST($name);
	}elsif($type eq 'check'){
		$out=$self->processCHECK($name);
	}elsif($type eq 'radiogroup'){
		$out=$self->processRADIOGROUP($name);
	}elsif($type eq 'radio'){
		$out=$self->processRADIO($name,$add_params);
	}elsif($type eq 'button' || $type eq 'submit'){
		$out=$self->processBUTTON($type,$name);
	}
	if ($self->{ERROR}{$name}){
		if ($self->{ERROR_AFTER_INPUT}){
			unless ($self->{ERROR_IN_TEXT}{$name}){
				$out.=$self->_GetErrorAfterInput($name) ;
			}
		}
	}
	return $out;
}
sub _GetErrorAfterInput{
	my $self=shift;
	my $name=shift;
	my $in_place=shift;
	return "" unless(length($self->{ERROR}{$name}));
	my $err=$self->{ERROR}{$name};
	return "" if ($err eq " ");
	my $templ;
	$templ=$self->{ERROR_AFTER_TEMPL} unless $in_place;
	$templ=$self->{ERROR_AFTER_TEMPL_INPLACE} if $in_place;
	$templ=~s/###ERR###/$err/;
	if($in_place){
		$self->{ERROR_IN_TEXT}{$name}=1;
	}
	return ($templ);	
}
###
sub set_def{
	my $self=shift;
	my $name=shift;
	my $val=shift;
	$self->{DEFAULT}{$name}=$val;
}
####
sub set_input{
	my $self=shift;
	my $name=shift;
	my $h_val=shift;
	my %val=%$h_val;
	foreach (keys %val){
		$self->{INPUT}{$name}{$_}=$val{$_}
	}
}
#####
sub add_element{
	my $self=shift;
	my $name=shift;
	my $value=shift;
	my $discr=shift;
	$discr=$value unless $discr;
	push @{$self->{INPUT}{$name}{'values'}}, $value;
	$self->{INPUT}{$name}{'labels'}{$value}=$discr;
}
#####
sub set_error{
	my $self=shift;
	my $name=shift;
	my $err=shift;
	$self->{ERROR}{$name}=$err;
}
#####
sub is_error{
	my $self = shift;
	my %errors;
	%errors=%{$self->{ERROR}} if exists($self->{ERROR});
	my $count=keys %errors;
	return $count;
}
######
#
sub ParseString{
	my $self=shift;
	s#\{er_([^\s_}]+)\}#_GetErrorAfterInput($self,$1,1)#ge;
	my $regesp=qr/{fm_[a-z]+_[^}]+\}/;
	s#($regesp)#ProcessElement($self,$1)#ge;
}
1;




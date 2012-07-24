#!/usr/bin/perl
######################################################################
# Database functions module                                          #
# Version 1.0    	                                                           #
# Last modified 16/12/2002                                         #
######################################################################
# PS. You must define $db variable as ref to DBI database
######################################################################
package dbfunc;
require Exporter;
use DBI;
@ISA = qw(Exporter);
@EXPORT=qw($db 
ColumnsInfo 
IsIndexExists 
IsColumnExists 
IsTableExists 
IndexInfo 
Error 
GetLastInsert 
GetSQLCount 
select_one_db 
update_db 
insert_db 
multiSQL
);
# $db  must be defined as DBI object
###################
sub multiSQL{
	my $sql=shift;
	my @str=split(/\n/,$sql);
	chomp @str;
	foreach(@str){
		s/^#.*//;
		s/;(\W)*$/ \n/;
	}
	my $SQL=join(" ",@str);
	@str=split(/\n/,$SQL);
	foreach (@str){
		$db->do($_);
		&Error;
	}
}
######################
sub GetSQLCount{
	my $sql=shift;
	$sql =~ s/\blimit\b.*$//i;
	$sql=~s/select\b.*?\bfrom/SELECT count(*) AS count FROM/i;
	my $out=$db->prepare($sql);
	$out->execute(@_);
	&Error($sql);
	my $hr = $out->fetchrow_hashref;	
	return $hr->{count};
}
###################
sub select_one_db{
	my $sql=shift;
	my @args=@_;
	my $out=$db->prepare($sql);
	$out->execute(@args);
	&Error($sql);
	return $out->fetchrow_hashref;
}
###################
sub insert_db{
	my $table=shift;
	my $h_ref=shift;
	my $funk_ref=shift;
	$funk_ref = {} unless defined $funk_ref;	
	$sql="SHOW columns FROM $table";
	my $out=$db->prepare($sql);
	$out->execute();
	my %defaults;
	while (my @output=@{$out->fetchrow_arrayref}){
		$defaults{$output[0]}=$output[4];
	}
	my %col=();#=%{$h_ref};
	map{$col{$_}=$h_ref->{$_}}keys %{$h_ref};
	map{$col{$_}=$funk_ref->{$_}}keys %{$funk_ref};
	my @args, @cols;
	@args=();
	@cols=();
	foreach (sort {$a cmp $b} keys %col){
		if ($col{$_} eq ''){
			$col{$_}=$defaults{$_};
		}
		push (@cols,"`$_`");
		unless(exists($funk_ref->{$_})){
			push (@args,$db->quote($col{$_}));
		}else{
			push (@args,$col{$_});
		}

	}
	my $last=GetLastInsert($table);

	my $sql="INSERT INTO $table  (".join(" , ",@cols).") VALUES (".join(" , ",@args).") ";
	if($db->do($sql)){
		return $db->{'mysql_insertid'};
	}else{
		&Error($sql);
		return 0;
	}
}
###################
sub update_db{
	my $table=shift;
	my $h_ref=shift;
	my $w_ref=shift;
	my $funk_ref=shift;
	$funk_ref = {} unless defined $funk_ref;
	$sql="SHOW columns FROM $table";
	my $out=$db->prepare($sql);
	$out->execute();
	my %defaults;
	while (my @output=@{$out->fetchrow_arrayref}){
		$defaults{$output[0]}=$output[4];
	}
	#my %col=%{$h_ref};
	my %col=();#=%{$h_ref};
	map{$col{$_}=$h_ref->{$_}}keys %{$h_ref};
	map{$col{$_}=$funk_ref->{$_}}keys %{$funk_ref};
	
	my %where=%{$w_ref};
	my @set,@where;
	@set=();
	@where=();
	foreach (sort {$a cmp $b} keys %col){
		#set default
		if ($col{$_} eq ''){
			$col{$_}=$defaults{$_};
		}
		unless(exists($funk_ref->{$_})){
			push (@set,"`$_`=".$db->quote($col{$_}));
		}else{
			push (@set,"`$_`=".$col{$_});
		}
	}
	foreach (sort {$a cmp $b} keys %where){
		push (@where,"`$_`=".$db->quote($where{$_}));
	}
	my $sql="UPDATE $table SET ".join(" , ",@set)." WHERE ".join(" AND ",@where); 
	my $res=$db->do($sql);
	&Error($sql);
	return $res;
}
###############################
sub Error{
	my $sql=shift;
#	print $q->header if $DBI::err;
	die "SQL error: \n $sql \n : ERROR: $DBI::err - $DBI::errstr" if $DBI::err;
}
###################
sub GetLastInsert{
	my %stolbs;
	my $sql="show table status  like ?";
	my $out=$db->prepare($sql);
	$out->execute($_[0]);
	&Error($sql);
	%stolbs=%{$out->fetchrow_hashref};
	my %newst;
	map{$newst{lc($_)}=$stolbs{$_}}keys %stolbs;
	return $newst{auto_increment};
}
#################

#################
sub IsTableExists{
	my $table=shift;
	my $sql="show table status  like ?";
	my $out=$db->prepare($sql);
	my %stolbs;
	$out->execute($table);
	return 1 if $out->rows;
	return 0;
}

sub IsColumnExists{
	my $table=shift;
	my $column=shift;
	my %info=ColumnsInfo($table);
	return exists $info{$column};
}
sub ColumnsInfo{
	#Field  Type  Null  Key  Default  Extra  Privileges  
	my $table=shift;
	my $sql="SHOW COLUMNS FROM `$table`";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my %info;
	while(my $output=$out->fetchrow_hashref){
		my $field=$output->{Field};
		delete($output->{Field}); 
		$info{$field}=$output;
	}
	return %info;
}
sub IsIndexExists{
	my $table=shift;
	my $index=shift;
	my %info=IndexInfo($table);
	if(exists($info{$index})){
		return 1;
	}else{
		return 0;
	}
}
sub IndexInfo{
	my $table=shift;
	my $sql="SHOW INDEX FROM `$table`";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my %info;
	while(my $output=$out->fetchrow_hashref){
		$info{$output->{Key_name}}{$output->{Column_name}}=1;
	}
	return %info;
}

#################
1;
#################

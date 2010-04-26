#!/usr/bin/perl
use POSIX qw(setsid);
my $word = $ARGV[0] or die "Usage:searchwork.pl word outfile\n";
my $outfile = $ARGV[1] or die "Usage:searchwork.pl word outfile\n";
print STDERR "starting parent process.\n";
&daemonize;
open(SEARCH, "| search4 --ascii --limit 1000000 /var/lib/philologic/databases/mvotest5/ > $outfile");
print SEARCH "$word\n";
close(SEARCH);

exit;

sub daemonize {
#    chdir '/'                 or die "Can't chdir to /: $!";
    open STDIN, '/dev/null'   or die "Can't read /dev/null: $!";
    open STDOUT, '>>/dev/null' or die "Can't write to /dev/null: $!";
    open STDERR, '>>/dev/null' or die "Can't write to /dev/null: $!";
    defined(my $childpid = fork)   or die "Can't fork: $!";
    if ($childpid) {
	print STDERR "[parent process exiting]\n";
	exit;
    }
    setsid                    or die "Can't start a new session: $!";
    print STDERR "Child detached from terminal\n";
    defined(my $grandchildpid = fork) or die "Can't fork: $!";
    if ($grandchildpid) {
	print STDERR "[child process exiting]\n";
	exit;
    }


    umask 0;
}

